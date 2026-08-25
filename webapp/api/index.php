<?php
// Bulletproof API Bridge for Shared Hosting on xuss.us
ini_set('display_errors', 0);
error_reporting(0);
set_time_limit(0);
ini_set('max_execution_time', 0);

// Determine the target API endpoint
$endpoint = $_GET['endpoint'] ?? '';
if (!$endpoint) {
    $uri = $_SERVER['REQUEST_URI'] ?? '';
    if (preg_match('#/api/([a-zA-Z0-9_\-]+)#', $uri, $matches)) {
        $endpoint = $matches[1];
    }
}
$endpoint = trim($endpoint, '/');
if (!$endpoint) {
    $endpoint = 'info';
}

// Forward to local Python FastAPI backend
$queryString = $_SERVER['QUERY_STRING'] ?? '';
// Remove endpoint parameter from query string if present
$cleanQuery = preg_replace('/(&?endpoint=[^&]*)/', '', $queryString);
$cleanQuery = trim($cleanQuery, '&');

$targetUrl = 'http://127.0.0.1:8000/api/' . $endpoint . ($cleanQuery ? '?' . $cleanQuery : '');

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $targetUrl);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_TIMEOUT, 120);
curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 15);
curl_setopt($ch, CURLOPT_CUSTOMREQUEST, $_SERVER['REQUEST_METHOD'] ?? 'GET');

$headers = ['Content-Type: application/json'];
if (!empty($_SERVER['HTTP_AUTHORIZATION'])) {
    $headers[] = 'Authorization: ' . $_SERVER['HTTP_AUTHORIZATION'];
}
curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);

if (in_array($_SERVER['REQUEST_METHOD'] ?? 'GET', ['POST', 'PUT', 'PATCH'])) {
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
