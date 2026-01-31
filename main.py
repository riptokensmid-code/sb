import discord
from discord.ext import commands


bot = commands.Bot(command_prefix='.', intents=intents, self_bot=False)

# Dictionary to store user-specific emoji preferences
user_emojis = {}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    
    # Start streaming "m"
    activity = discord.Streaming(
        name="m",
        url="https://www.twitch.tv/directory"
    )
    await bot.change_presence(activity=activity)
    print('Now streaming "m"!')

@bot.command(name='r')
async def set_reaction(ctx, emoji: str = None):
    """
    Set an emoji to react to all your messages with.
    Usage: .r <emoji> or .r to clear
    """
    user_id = ctx.author.id
    
    if emoji is None:
        # Clear the reaction setting
        if user_id in user_emojis:
            del user_emojis[user_id]
            await ctx.send(f'✅ Reaction setting cleared! I will no longer react to your messages.')
        else:
            await ctx.send(f'❌ You don\'t have an active reaction setting. Use `.r <emoji>` to set one.')
        return
    
    # Validate emoji (check if it's a custom emoji or a default one)
    try:
        # Try to convert to emoji (for custom emojis)
        if emoji.startswith('<') and emoji.endswith('>'):
            # Custom emoji format: <:name:id>
            emoji_id = int(emoji.split(':')[2][:-1])
            emoji_obj = bot.get_emoji(emoji_id)
            if not emoji_obj:
                await ctx.send(f'❌ I cannot access that custom emoji. Make sure I\'m in the server where it exists.')
                return
        else:
            # Default emoji - try to react with it to test
            test_msg = await ctx.send('Testing emoji...')
            try:
                await test_msg.add_reaction(emoji)
                await test_msg.delete()
            except:
                await ctx.send(f'❌ Invalid emoji. Please use a valid emoji that I can use.')
                return
        
        # Store the emoji for this user
        user_emojis[user_id] = emoji
        await ctx.send(f'✅ I will now react to all your messages with {emoji}')
        
    except Exception as e:
        await ctx.send(f'❌ Error setting emoji: {str(e)}')

@bot.event
async def on_message(message):
    # Don't react to bot messages (including our own)
    if message.author.bot:
        await bot.process_commands(message)
        return
    
    # Check if the author has an emoji set
    user_id = message.author.id
    if user_id in user_emojis:
        try:
            # Try to react with the stored emoji
            await message.add_reaction(user_emojis[user_id])
        except discord.HTTPException:
            # If reaction fails (emoji invalid or missing), clear the setting
            try:
                del user_emojis[user_id]
            except KeyError:
                pass
    
    # Process commands
    await bot.process_commands(message)

@bot.command(name='rlist')
async def list_reactions(ctx):
    """List all active reaction settings"""
    if not user_emojis:
        await ctx.send('No active reaction settings.')
        return
    
    embed = discord.Embed(title="Active Reaction Settings", color=discord.Color.blue())
    for user_id, emoji in user_emojis.items():
        user = bot.get_user(user_id)
        username = user.name if user else f"Unknown User ({user_id})"
        embed.add_field(name=username, value=f"Emoji: {emoji}", inline=False)
    
    await ctx.send(embed=embed)

# Optional: Command to change streaming text
@bot.command()
async def stream(ctx, *, text: str = "m"):
    """Change the streaming text"""
    activity = discord.Streaming(
        name=text,
        url="https://www.twitch.tv/directory"
    )
    await bot.change_presence(activity=activity)
    await ctx.send(f'Now streaming "{text}"!')

# Run the bot
bot.run('MTQ2NzA4MTI1MzIyMzE0MTQwNg.Gs1rzE.hT0E5TD3JIyRMgud1XXOAMsxPH3s1wKYIpPZcE')
