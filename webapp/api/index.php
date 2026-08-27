<?php
// Unified High-Performance API Proxy for xuss.us LiteSpeed/Apache
ini_set('display_errors', 0);
error_reporting(0);
set_time_limit(0);
ini_set('max_execution_time', 0);

// Set CORS headers for Mini App
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With");

if (isset($_SERVER['REQUEST_METHOD']) && strtoupper($_SERVER['REQUEST_METHOD']) === 'OPTIONS') {
    http_response_code(200);
    exit;
}

// Determine the target API endpoint
$endpoint = $_GET['endpoint'] ?? '';
if (!$endpoint) {
    $uri = $_SERVER['REQUEST_URI'] ?? '';
    $path = parse_url($uri, PHP_URL_PATH);
    if (preg_match('#/api/([a-zA-Z0-9_\-]+)#', $path, $matches)) {
        $endpoint = $matches[1];
    }
}
$endpoint = trim($endpoint, '/');
if (!$endpoint) {
    $endpoint = 'info';
}

// Forward to local Python FastAPI backend
$queryString = $_SERVER['QUERY_STRING'] ?? '';
$cleanQuery = preg_replace('/(&?endpoint=[^&]*)/', '', $queryString);
$cleanQuery = trim($cleanQuery, '&');

$targetUrl = 'http://127.0.0.1:8000/api/' . $endpoint . ($cleanQuery ? '?' . $cleanQuery : '');
$method = strtoupper($_SERVER['REQUEST_METHOD'] ?? 'GET');

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $targetUrl);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
curl_setopt($ch, CURLOPT_POSTREDIR, 7); // Preserve POST across 301, 302, 307 redirects
curl_setopt($ch, CURLOPT_MAXREDIRS, 5);
curl_setopt($ch, CURLOPT_TIMEOUT, 180);
curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 15);
curl_setopt($ch, CURLOPT_CUSTOMREQUEST, $method);

$headers = ['Content-Type: application/json'];
if (!empty($_SERVER['HTTP_AUTHORIZATION'])) {
    $headers[] = 'Authorization: ' . $_SERVER['HTTP_AUTHORIZATION'];
}
curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);

if (in_array($method, ['POST', 'PUT', 'PATCH'])) {
    $body = file_get_contents('php://input');
    curl_setopt($ch, CURLOPT_POSTFIELDS, $body);
}

$response = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$curlErr = curl_error($ch);
curl_close($ch);

if ($curlErr || $response === false) {
    http_response_code(502);
    header('Content-Type: application/json');
    echo json_encode([
        'detail' => 'Python server ishlamayapti. Terminalda "nohup python3 main.py > bot.log 2>&1 &" buyrug\'ini bering.'
    ]);
    exit;
}

http_response_code($httpCode ?: 200);
header('Content-Type: application/json');
echo $response;
?>
