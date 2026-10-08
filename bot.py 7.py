import os
import threading
from flask import Flask

app = Flask('')

@app.route('/')
def home():
    return "Bot Online!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

threading.Thread(target=run).start()

# 1. CONFIGURAÇÃO DO BOT E MEMÓRIA TEMPORÁRIA
bot = commands.Bot(command_prefix=["!", "?", "."], intents=discord.Intents.all())

# Dicionário para guardar os links na memória do bot (valores padrão)
links_config = {
    "lobby": "https://steampowered.com",
    "individuais": [
        "https://link1.com",
        "https://link2.com",
        "https://link3.com"
    ]
}

# 2. PAINEL INTERATIVO (VIEW COM BOTÕES)
class PainelGames(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Lobby 🏠", style=discord.ButtonStyle.blurple, disabled=True)
    async def botao_lobby(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Você já está no Lobby!", ephemeral=True)

    @discord.ui.button(label="Links Individuais 🔒", style=discord.ButtonStyle.green)
    async def botao_premium(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Verifica se o utilizador tem o cargo "Premium"
        tem_cargo_premium = any(role.name == "Premium" for role in interaction.user.roles)
        
        if tem_cargo_premium:
            # Junta todos os links guardados na configuração
            lista_links = "\n".join([f"🔗 [Link {i+1}]({link})" for i, link in enumerate(links_config["individuais"])])
            
            embed_premium = discord.Embed(
                title="🎯 Links Individuais Premium",
                description=f"Aqui estão os seus links exclusivos:\n\n{lista_links}",
                color=discord.Color.gold()
            )
            await interaction.response.send_message(embed=embed_premium, ephemeral=True)
        else:
            await interaction.response.send_message("❌ Este botão é exclusivo para membros com o cargo **@Premium**!", ephemeral=True)

    @discord.ui.button(label="Coming Soon... ⏳", style=discord.ButtonStyle.gray, disabled=True)
    async def botao_futuro(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass

# 3. FUNÇÃO PARA GERAR O EMBED DO LOBBY
def criar_embed_lobby():
    link_atual = links_config["lobby"]
    embed = discord.Embed(
        title="🎮 Painel de Jogos",
        description=f"Bem-vindo ao Lobby! Aqui está o link principal do jogo:\n\n🔗 **[CLIQUE AQUI PARA JOGAR]({link_atual})**",
        color=discord.Color.blue()
    )
    embed.set_footer(text="Selecione uma opção abaixo para navegar.")
    return embed

# 4. EVENTO: QUANDO O BOT LIGA
@bot.event
async def on_ready():
    print(f"Bot online como {bot.user}!")
    try:
        sincronizados = await bot.tree.sync()
        print(f"Sincronizados {len(sincronizados)} comandos de barra!")
    except Exception as e:
        print(f"Erro ao sincronizar: {e}")



@bot.command(name="link")
async def comando_texto_link(ctx, *, subcomando: str = ""):
    if subcomando.lower() == "games":
        embed = criar_embed_lobby()
        view = PainelGames()
        await ctx.send(embed=embed, view=view)


@bot.tree.command(name="link", description="Abre o painel de jogos.")
async def comando_barra_link(interaction: discord.Interaction, subcomando: str):
    if subcomando.lower() == "games":
        embed = criar_embed_lobby()
        view = PainelGames()
        await interaction.response.send_message(embed=embed, view=view)
    else:
        await interaction.response.send_message("Use `/link games` para abrir o painel correto.", ephemeral=True)



class GrupoConfig(app_commands.Group):
    def __init__(self):
        super().__init__(name="config", description="Comandos de configuração do Painel")

    # /config lobby [link] (Apenas Admin)
    @app_commands.command(name="lobby", description="Altera o link principal do Lobby.")
    @app_commands.checks.has_permissions(administrator=True)
    async def config_lobby(self, interaction: discord.Interaction, link: str):
        links_config["lobby"] = link
        await interaction.response.send_message(f"✅ O link do Lobby foi atualizado para: {link}", ephemeral=True)

    
    @app_commands.command(name="links_individuais", description="Altera os 3 links premium.")
    @app_commands.checks.has_permissions(administrator=True)
    async def config_individuais(self, interaction: discord.Interaction, link1: str, link2: str, link3: str):
        links_config["individuais"] = [link1, link2, link3]
        await interaction.response.send_message(
            f"✅ Os links individuais foram atualizados!\n1️⃣ {link1}\n2️⃣ {link2}\n3️⃣ {link3}", 
            ephemeral=True
        )

    # Tratamento de erro caso alguém tente usar sem ser Admin
    @config_lobby.error
    @config_individuais.error
    async def config_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("❌ Apenas membros com a permissão de **Administrador** podem usar este comando.", ephemeral=True)


bot.tree.add_command(GrupoConfig())

bot.run(os.getenv('DISCORD_TOKEN')')
