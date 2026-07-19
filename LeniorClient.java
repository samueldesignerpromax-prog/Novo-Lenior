// LeniorClient.java
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.Base64;
import java.util.Scanner;

public class LeniorClient {

    private static final String API_BASE = "https://lenior-api-1-hvvj.onrender.com";
    private static final String TEXT_ENDPOINT = API_BASE + "/chat/texto";
    private static String sessaoId = null;

    public static void main(String[] args) throws Exception {
        HttpClient client = HttpClient.newBuilder()
                .connectTimeout(Duration.ofSeconds(10))
                .build();

        System.out.println("🧠 Lenior 2.0 — Cliente Java");
        System.out.println("Digite 'sair' para encerrar.\n");

        try (Scanner scanner = new Scanner(System.in)) {
            while (true) {
                System.out.print("Você: ");
                String pergunta = scanner.nextLine().trim();
                if (pergunta.isEmpty()) continue;
                if (pergunta.equalsIgnoreCase("sair") || pergunta.equalsIgnoreCase("quit")) {
                    System.out.println("Até logo!");
                    break;
                }

                String jsonPayload = String.format("{\"texto\": \"%s\"%s}",
                        pergunta.replace("\"", "\\\""),
                        sessaoId != null ? ", \"sessao_id\": \"" + sessaoId + "\"" : "");

                HttpRequest request = HttpRequest.newBuilder()
                        .uri(URI.create(TEXT_ENDPOINT))
                        .header("Content-Type", "application/json")
                        .POST(HttpRequest.BodyPublishers.ofString(jsonPayload))
                        .timeout(Duration.ofSeconds(30))
                        .build();

                try {
                    HttpResponse<String> response = client.send(request,
                            HttpResponse.BodyHandlers.ofString());

                    if (response.statusCode() != 200) {
                        System.out.println("❌ Erro HTTP " + response.statusCode());
                        System.out.println(response.body());
                        continue;
                    }

                    String body = response.body();
                    String texto = extrairCampo(body, "\"texto\"");
                    String audioBase64 = extrairCampo(body, "\"audio\"");
                    String novaSessao = extrairCampo(body, "\"sessao_id\"");

                    if (novaSessao != null && !novaSessao.isEmpty()) {
                        sessaoId = novaSessao;
                    }

                    System.out.println("Lenior: " + (texto != null ? texto : "(vazio)"));

                    if (audioBase64 != null && !audioBase64.isEmpty()) {
                        byte[] audioBytes = Base64.getDecoder().decode(audioBase64);
                        String nomeArq = "resposta_java.wav";
                        java.nio.file.Files.write(java.nio.file.Paths.get(nomeArq), audioBytes);
                        System.out.println("✅ Áudio salvo em: " + nomeArq);
                    }

                    if (body.contains("\"execucao\"")) {
                        String exec = extrairCampo(body, "\"execucao\"");
                        System.out.println("🧪 Execução: " + (exec != null ? exec : "(sem detalhes)"));
                    }

                } catch (Exception e) {
                    System.err.println("❌ Erro: " + e.getMessage());
                }
                System.out.println();
            }
        }
    }

    private static String extrairCampo(String json, String chave) {
        String busca = "\"" + chave + "\":";
        int idx = json.indexOf(busca);
        if (idx < 0) return null;
        int ini = idx + busca.length();
        while (ini < json.length() && Character.isWhitespace(json.charAt(ini))) ini++;
        if (ini >= json.length()) return null;
        char primeiro = json.charAt(ini);
        if (primeiro == '"') {
            int fim = ini + 1;
            while (fim < json.length() && json.charAt(fim) != '"') fim++;
            if (fim < json.length()) {
                return json.substring(ini + 1, fim);
            }
            return null;
        } else if (primeiro == '{' || primeiro == '[') {
            int profundidade = 0;
            int fim = ini;
            do {
                char c = json.charAt(fim);
                if (c == '{' || c == '[') profundidade++;
                else if (c == '}' || c == ']') profundidade--;
                fim++;
            } while (fim < json.length() && profundidade > 0);
            return json.substring(ini, fim);
        } else {
            int fim = ini;
            while (fim < json.length() && ",}] \t\n\r".indexOf(json.charAt(fim)) < 0) fim++;
            return json.substring(ini, fim);
        }
    }
}
