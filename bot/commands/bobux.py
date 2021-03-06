from ..betterbot import Member
import discord
import db

name = 'bobux'


async def run(message, member: Member = None):
	if not member:
		member = message.author
	bobux = await db.get_bobux(member.id)
	if member.id == message.author.id:
		bobux_message = f'You have **{bobux}** bobux'
	else:
		bobux_message = f'<@{member.id}> has **{bobux}** bobux'
	embed = discord.Embed(
		description=bobux_message
	)
	await message.channel.send(embed=embed)
