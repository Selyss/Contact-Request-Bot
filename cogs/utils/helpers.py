import nextcord


async def create_ticket(
    inter: nextcord.Interaction, person: nextcord.Member, category
) -> nextcord.TextChannel:
    category = nextcord.utils.get(inter.guild.categories, id=category)
    new_channel: nextcord.TextChannel = await category.create_text_channel(
        name=f"ticket-{person.name}",
        reason=f"Created ticket for {person.id} - {person.name}",
        topic=id,
    )
    await inter.response.send_message(
        f"Ticket created: <#{new_channel.id}>", ephemeral=True
    )
    return new_channel
