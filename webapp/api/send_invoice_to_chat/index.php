<?php
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

$backend_url = "http://127.0.0.1:8000/api/send_invoice_to_chat";

$input = file_get_contents('php://input');

$ch = curl_init($backend_url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_CUSTOMREQUEST, $_SERVER['REQUEST_METHOD']);

if (!empty($input)) {
    curl_setopt($ch, CURLOPT_POSTFIELDS, $input);
    curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type: application/json'));
}

$response = curl_exec($ch);
$http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$content_type = curl_getinfo($ch, CURLINFO_CONTENT_TYPE);

if (curl_errno($ch)) {
    http_response_code(502);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode(["detail" => "Python FastAPI serveriga ulanishda xatolik (Port 8000)."]);
    curl_close($ch);
    exit;
}

curl_close($ch);

http_response_code($http_code);
if ($content_type) {
    header("Content-Type: $content_type");
} else {
    header("Content-Type: application/json; charset=utf-8");
}

echo $response;
