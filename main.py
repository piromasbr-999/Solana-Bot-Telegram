import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from webacy_client import check_address_risk, check_url_risk

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Configuração simples de logs no terminal
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    welcome_text = (
        "🛡️ **Solana Shield Bot**\n\n"
        "Envie um endereço de carteira, token da Solana ou link para verificar o nível de risco.\n\n"
        "**Comandos disponíveis:**\n"
        "• `/check <endereço_solana>` - Analisa o risco de um endereço ou token.\n"
        "• `/checkurl <link>` - Verifica se um site é phishing ou wallet drainer. \n"
        "\n"
        "\n"
        "BY -- PIROMASBR (:"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /check <endereço>"""
    if not context.args:
        await update.message.reply_text("⚠️ Informe o endereço da Solana.\nExemplo: `/check 7xKX...39aB`", parse_mode="Markdown")
        return

    address = context.args[0]
    await update.message.reply_text(f"🔍 Analisando endereço na Solana: `{address}`...", parse_mode="Markdown")

    # Chamada para o módulo que consome a API da Webacy
    risk_data = await check_address_risk(address)

    if not risk_data:
        await update.message.reply_text("❌ Não foi possível obter os dados de risco para este endereço no momento.")
        return

    # Extrai o score ou flags retornadas pela Webacy
    score = risk_data.get("risk_score", 0)
    flags = risk_data.get("flags", [])

    # Formatação da resposta
    if score > 70:
        status_emoji = "🔴"
        risk_level = "ALTO RISCO"
    elif score > 30:
        status_emoji = "🟡"
        risk_level = "MÉDIO RISCO"
    else:
        status_emoji = "🟢"
        risk_level = "SEGURO / BAIXO RISCO"

    flags_text = "\n".join([f"• 🚩 {flag}" for flag in flags]) if flags else "• Nenhum alerta crítico encontrado."

    response = (
        f"🛡️ **Solana Shield — Análise de Risco**\n\n"
        f"**Endereço:** `{address}`\n"
        f"**Status:** {status_emoji} **{risk_level}** (Score: {score}/100)\n\n"
        f"**Alertas Encontrados:**\n{flags_text}"
    )

    await update.message.reply_text(response, parse_mode="Markdown")

async def checkurl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /checkurl <url>"""
    if not context.args:
        await update.message.reply_text("⚠️ Informe a URL que deseja verificar.\nExemplo: `/checkurl https://exemplo.com`", parse_mode="Markdown")
        return

    url = context.args[0]
    await update.message.reply_text(f"🔍 Verificando URL: `{url}`...", parse_mode="Markdown")

    url_data = await check_url_risk(url)

    if not url_data:
        await update.message.reply_text("❌ Não foi possível verificar esta URL no momento.")
        return

    is_malicious = url_data.get("is_malicious", False)
    
    if is_malicious:
        response = f"🛡️ **Solana Shield — Verificação de URL**\n\n**Link:** `{url}`\n**Status:** ⛔ **MALICIOSO / DRAINER**\n\n🛑 *Este site foi classificado como Phishing pela Webacy Engine.*"
    else:
        response = f"🛡️ **Solana Shield — Verificação de URL**\n\n**Link:** `{url}`\n**Status:** 🟢 **NENHUMA AMEAÇA DETECTADA**"

    await update.message.reply_text(response, parse_mode="Markdown")

def main():
    """Inicializa o bot no Telegram"""
    if not TELEGRAM_TOKEN:
        print("Erro: TELEGRAM_BOT_TOKEN não configurado no arquivo .env")
        return

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Registra os handlers dos comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check))
    app.add_handler(CommandHandler("checkurl", checkurl))

    print("🤖 Bot rodando...")
    app.run_polling()

if __name__ == "__main__":
    main()