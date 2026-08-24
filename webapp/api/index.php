<?php
// Bulletproof PHP Proxy for CGI/FastCGI/Apache/Nginx on Shared Hostings
ini_set('display_errors', 0);
error_reporting(0);

$requestUri = $_SERVER['REQUEST_URI'] ?? '/api';
$targetUrl = 'http://127.0.0.1:8000' . $requestUri;

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $targetUrl);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_TIMEOUT, 90);
curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 10);
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
        'detail' => 'Python backend serverga ulanib bo\'lmadi. Terminalda "nohup python3 main.py > bot.log 2>&1 &" ishlab turganini tekshiring.'
    ]);
    exit;
}

http_response_code($httpCode ?: 200);
header('Content-Type: application/json');
echo $response;
?>
