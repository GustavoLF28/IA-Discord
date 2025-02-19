import discord
from discord.ext import commands
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from langdetect import detect

# Carregar o modelo e o tokenizer para o português
tokenizer = GPT2Tokenizer.from_pretrained("pierreguillou/gpt2-small-portuguese")
model = GPT2LMHeadModel.from_pretrained("pierreguillou/gpt2-small-portuguese")


# Defina o token do seu bot do Discord
DISCORD_TOKEN = ""  # Substitua com o token do seu bot

# Cria a instância do bot do Discord
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def query_gpt2_local(prompt):
    # Detecta o idioma da pergunta
    detected_language = detect(prompt)
    
    # Se o idioma não for português, reformula o prompt para forçar a resposta em português
    if detected_language != 'pt':
        prompt = f"Responda em português: {prompt}"

    # Tokeniza a entrada
    inputs = tokenizer.encode(prompt, return_tensors="pt")

    # Gera a resposta com parâmetros ajustados para mais coerência
    outputs = model.generate(
        inputs,
        max_length=100,  # Tamanho máximo da resposta
        num_return_sequences=1,  # Número de respostas a gerar
        no_repeat_ngram_size=2,  # Evita repetições no texto gerado
        temperature=0.7,  # Menos aleatório, mais coerente
        top_p=0.9,  # Limita a diversidade
        top_k=50  # Limita o número de palavras a considerar
    )

    # Decodifica a saída gerada
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response

# Evento para quando o bot estiver pronto
@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user.name}')

# Evento para quando o bot receber uma mensagem
@bot.event
async def on_message(message):
    # Não responda a si mesmo
    if message.author == bot.user:
        return

    if message.content.startswith('!'):
        question = message.content[len('!'):].strip()  # Remove o comando "!" da mensagem
        print(f"Recebendo pergunta: {question}")

        # Usando GPT-2 para gerar a resposta
        response = query_gpt2_local(question)
        print(f"Resposta gerada: {response}")

        # Envia a resposta gerada para o Discord
        await message.channel.send(response)

# Inicia o bot
bot.run(DISCORD_TOKEN)