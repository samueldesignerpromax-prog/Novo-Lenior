#!/usr/bin/env ruby
# lenior_ruby.rb
# Uso: ruby lenior_ruby.rb "sua pergunta"

require 'net/http'
require 'json'
require 'base64'

API_URL = 'https://novo-lenior.onrender.com/chat/texto'
# ... resto igual

pergunta = ARGV[0] || 'Olá'

uri = URI(API_URL)
req = Net::HTTP::Post.new(uri)
req['Content-Type'] = 'application/json'
req.body = { texto: pergunta }.to_json

begin
  res = Net::HTTP.start(uri.hostname, uri.port, use_ssl: true) do |http|
    http.request(req)
  end

  if res.code.to_i != 200
    puts "❌ Erro HTTP #{res.code}"
    puts res.body
    exit 1
  end

  data = JSON.parse(res.body)
  puts "🧠 Você: #{pergunta}"
  puts "🤖 Lenior: #{data['texto']}"

  if data['audio']
    audio_bytes = Base64.decode64(data['audio'])
    File.open('resposta_ruby.wav', 'wb') { |f| f.write(audio_bytes) }
    puts "✅ Áudio salvo em: resposta_ruby.wav"
  end

  if data['execucao']
    puts "🧪 Execução: #{JSON.pretty_generate(data['execucao'])}"
  end

rescue => e
  puts "❌ Erro: #{e.message}"
end
