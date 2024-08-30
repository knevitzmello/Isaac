import spotipy
from spotipy.oauth2 import SpotifyOAuth

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="5086fd3d57a448a99ac860d2edbff6cb",
    client_secret="0201a2f8b7f341b88181a64af81a8d61",
    redirect_uri="http://localhost:5000/callback",
    scope="user-modify-playback-state user-read-playback-state"
))

results = sp.search(q="fred again", type="track", limit=1)
track = results['tracks']['items'][0]
print(f"Track found: {track['name']} by {track['artists'][0]['name']}")

devices = sp.devices()
print(devices)

device_name = "Web Player (Chrome)"
device_id = None
for device in devices['devices']:
    if device['name'] == device_name:
        device_id = device['id']
        break


if device_id:
    # Transferir a reprodução para o dispositivo desejado
    sp.transfer_playback(device_id=device_id, force_play=True)
    print(f"Transferência para o dispositivo '{device_name}' bem-sucedida.")
    
    # Iniciar reprodução da música
    sp.start_playback(device_id=device_id, uris=[track['uri']])
else:
    print(f"Dispositivo '{device_name}' não encontrado.")
#sp.start_playback(uris=[track['uri']])
