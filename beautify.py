import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
import requests
import time
import calendar

load_dotenv()
DISCORD_TOKEN = os.getenv("TOKEN")
DOTOKEN = os.getenv("DOTOKEN")
bot = commands.Bot(command_prefix="$")
fingerprints = [
    "01:44:4f:ad:32:e3:a1:39:ff:c5:26:c0:fb:67:fd:f2",
    "22:95:3b:04:17:4c:23:02:b2:c3:ab:b4:48:ee:30:ee"
]
server_ip = None


def get_json(method, url):
    bearer_token = "Bearer " + DOTOKEN
    headers = {
        'Content-Type': 'application/json',
        'Authorization': bearer_token
    }
    x = getattr(requests, method.lower())
    return x(url, headers=headers).json()


def get_droplet():
    saved_json = get_json(
        "GET", "https://api.digitalocean.com/v2/droplets?page=1&per_page=1")
    droplets = saved_json['droplets']
    el = [y for y in droplets if y["name"] == "valheim-fra1"][0]
    return el


def get_snapshots():
    saved_json = get_json(
        "GET",
        "https://api.digitalocean.com/v2/snapshots?resource_type=droplet")
    return saved_json["snapshots"]


def find_correct_snapshot_id(snapshots):
    potential_snapshots = [
        y for y in snapshots if not y["name"].find("valheim")
    ]
    print("potential_snapshots")
    print(potential_snapshots)
    print("SORTED")
    return sorted(potential_snapshots,
                  key=lambda item: item["created_at"],
                  reverse=True)[0]["id"]


def find_public_ip(droplet_id):
    droplet = get_droplet_by_id(droplet_id)
    print("\nTrying to find Public IP\n")
    try:
        public_ip = [
            y for y in droplet["networks"]["v4"] if y["type"] == "public"
        ][0]["ip_address"]
        if public_ip:
            print("\nFound Public IP\n")
            return public_ip
        raise
    except:
        print("\nCouldn't find Public IP. Retrying...\n")
        time.sleep(3)
        return find_public_ip(droplet_id)


def create_droplet(snapshot_id):
    bearer_token = "Bearer " + DOTOKEN
    headers = {
        'Content-Type': 'application/json',
        'Authorization': bearer_token
    }
    json_data = {
        "name": "valheim-fra1",
        "region": "fra1",
        "size": "s-2vcpu-4gb",
        "image": snapshot_id,
        "ssh_keys": fingerprints,
        "backups": False,
        "ipv6": False,
        "tags": ["valheim"]
    }
    post_response = requests.post(
        "https://api.digitalocean.com/v2/droplets?page=1&per_page=1",
        json=json_data,
        headers=headers)
    return post_response.json()["droplet"]


def get_droplet_by_id(droplet_id):
    saved_json = get_json(
        "GET", "https://api.digitalocean.com/v2/droplets/" + str(droplet_id))
    return saved_json["droplet"]


def wait_active_droplet(droplet_id):
    try:
        status = get_droplet_by_id(droplet_id)["status"]
        if not status == "active":
            print("\nStatus not yet active\n")
            raise
    except:
        time.sleep(2)
        return wait_active_droplet(droplet_id)


def init():
    droplet = get_droplet()
    if droplet:
        global server_ip
        server_ip = find_public_ip(droplet["id"])
        wait_active_droplet(droplet["id"])
    print("\nFinished init\n")


def create_snapshot(droplet_id):
    bearer_token = "Bearer " + DOTOKEN
    headers = {
        'Content-Type': 'application/json',
        'Authorization': bearer_token
    }
    json_data = {
        "type": "snapshot",
        "name": "valheim" + str(calendar.timegm(time.gmtime()))
    }
    post_response = requests.post("https://api.digitalocean.com/v2/droplets/" +
                                  str(droplet_id) + "/actions",
                                  json=json_data,
                                  headers=headers).json()
    snapshot_id = post_response["action"]["id"]
    try:
        while True:
            print("Trimis GET")
            get_response = get_json(
                "GET", "https://api.digitalocean.com/v2/droplets/" +
                       str(droplet_id) + "/actions")["actions"]
            good_snapshot = [
                y for y in get_response if y["id"] == snapshot_id
            ][0]
            if good_snapshot["status"] == "completed":
                print("Status Completed")
                return good_snapshot
            elif good_snapshot["status"] == "errored":
                print("Status Eroare")
                raise NameError('Snapshot Eroare')
            time.sleep(5)
    except Exception as e:
        raise e


def delete_droplet(droplet_id):
    bearer_token = "Bearer " + DOTOKEN
    headers = {
        'Content-Type': 'application/json',
        'Authorization': bearer_token
    }
    delete_response = requests.delete("https://api.digitalocean.com/v2/droplets/" + droplet_id, headers=headers)
    return delete_response.status_code == "204"


@bot.command(
    help=
    "Comanda folosita pentru a porni/opri/restarta serverul. Primeste argumentele : 'start', 'stop', 'restart', 'details' ",
    brief="Comanda Basic")
async def server(ctx, *args):
    global server_ip
    for arg in args:
        if arg == "wake":
            print("Incerc sa creez Droplet...")
            snapshots = get_snapshots()
            print("\nSnapshots: ", snapshots)
            correct_snapshot_id = find_correct_snapshot_id(snapshots)
            print("\nCorrect snapshot id: " + str(correct_snapshot_id))
            new_droplet = create_droplet(correct_snapshot_id)
            print("\nNew Droplet: ", new_droplet)
            new_droplet_id = new_droplet["id"]
            print("\nNew Droplet ID: " + str(new_droplet_id))
            server_ip = find_public_ip(new_droplet_id)
            print("\nPublic IP: " + str(server_ip))
            await ctx.channel.send("Am creat Droplet!")
            wait_active_droplet(new_droplet_id)
            await ctx.channel.send("Dropletul este gata!")

        elif arg == "sleep":
            print("NU")

        elif arg == "test1":
            create_snapshot(get_droplet()["id"])
            D

    if not server_ip:
        await ctx.channel.send("Nu am gasit Droplet!")
        return

    for arg in args:
        if arg == "start":
            await ctx.channel.send("Pornesc Serverul...")
            try:
                response = requests.get(f"http://{server_ip}:3000/cmd/start")
            except Exception as e:
                print(e)
                await ctx.channel.send("Frontendul lui David nu este activat")
                break
            await ctx.channel.send("Serverul a pornit pe IP-ul: " +
                                   str(server_ip))
            break

        elif arg == "stop":
            await ctx.channel.send("Opresc Serverul...")
            response = requests.get(f"http://{server_ip}:3000/cmd/stop")
            # await ctx.channel.send(response.json())
            await ctx.channel.send("Am oprit Serverul.")
            break

        elif arg == "details":
            await ctx.channel.send("trebuie sa detaliez")
            response = requests.get(f"http://{server_ip}:3000/cmd/details")
            break

        elif arg == "restart":
            await ctx.channel.send("trebuie sa restartez")
            response = requests.get(f"http://{server_ip}:3000/cmd/restart")
            break

        elif arg == "update":
            await ctx.channel.send("aici fac update")
            response = requests.get(f"http://{server_ip}:3000/cmd/update")
            break

        else:
            await ctx.channel.send("Comanda Invalida! Incearca: $help server")
            break


# await ctx.channel.send(response)


@bot.event
async def on_message(message):
    if message.content == "start":
        print("asd")
    await bot.process_commands(message)


@bot.event
async def on_ready():
    print('We have logged in as' + str(bot))
    init()


bot.run(DISCORD_TOKEN)
