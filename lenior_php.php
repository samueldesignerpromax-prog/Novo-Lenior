<?php
// lenior_php.php
// Uso: php lenior_php.php "sua pergunta"
// Ou via web: ?q=sua+pergunta

<?php
$api_url = "https://novo-lenior.onrender.com/chat/texto";
// ... resto igual

// Pega a pergunta da linha de comando ou GET
if (php_sapi_name() === 'cli') {
    $pergunta = $argv[1] ?? "Olá";
} else {
    $pergunta = $_GET["q"] ?? "Olá";
}

$payload = json_encode(["texto" => $pergunta]);

$ch = curl_init($api_url);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, $payload);
curl_setopt($ch, CURLOPT_HTTPHEADER, ["Content-Type: application/json"]);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_TIMEOUT, 30);

$resposta = curl_exec($ch);
$erro = curl_error($ch);
curl_close($ch);

if ($erro) {
    echo "❌ Erro: $erro\n";
    exit(1);
}

$data = json_decode($resposta, true);
if (!$data) {
    echo "❌ Erro ao decodificar JSON.\n";
    exit(1);
}

echo "🧠 Você: $pergunta\n";
echo "🤖 Lenior: " . ($data["texto"] ?? "(sem resposta)") . "\n";

if (!empty($data["audio"])) {
    $audioBytes = base64_decode($data["audio"]);
    file_put_contents("resposta_php.wav", $audioBytes);
    echo "✅ Áudio salvo em: resposta_php.wav\n";
}

if (!empty($data["execucao"])) {
    echo "🧪 Execução: " . json_encode($data["execucao"], JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE) . "\n";
}
?>
