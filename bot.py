import asyncio
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

is_timer_running = False


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")


def play_audio(vc, file_path, loop=False):
    if vc.is_playing():
        vc.stop()

    options = "-stream_loop -1" if loop else None

    vc.play(
        discord.FFmpegPCMAudio(file_path, options=options),
        after=lambda e: print(f"Finished: {e}") if e else None,
    )


@bot.command()
async def start(ctx):
    global is_timer_running

    if not ctx.author.voice:
        await ctx.send("❌ ボイスチャンネルに参加してください。")
        return

    channel = ctx.author.voice.channel
    if ctx.voice_client:
        vc = ctx.voice_client
        if vc.channel != channel:
            await vc.move_to(channel)
    else:
        vc = await channel.connect()

    if is_timer_running:
        await ctx.send("⏱️ タイマーは既に稼働しています。")
        return

    is_timer_running = True
    await ctx.send(
        "🚀 **ポモドーロタイマーを開始します。**\n⏱️ 25分間の集中タイムです。"
    )

    try:
        while is_timer_running:
            play_audio(vc, "lofi.mp3", loop=True)
            await asyncio.sleep(25 * 60)

            if not is_timer_running:
                break

            await ctx.send("🔔 **25分経ちました。** 5分間の休憩タイムです。")
            play_audio(vc, "alarm.mp3", loop=False)
            await asyncio.sleep(5 * 60)

            if not is_timer_running:
                break

            await ctx.send("🔄 **休憩終了です。** 集中タイムを再開します。")

    except asyncio.CancelledError:
        pass


@bot.command()
async def stop(ctx):
    global is_timer_running

    is_timer_running = False

    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.voice_client.disconnect()
        await ctx.send("🛑 タイマーを終了し、退出しました。")
    else:
        await ctx.send("❌ タイマーは動いていません。")
