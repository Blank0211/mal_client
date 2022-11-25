import sys
import json
import requests
from secrets import token_urlsafe
from pprint import pprint
CLIENT_ID = "d2b59caf73a52c2d8c6a5be3e7bd9733"


# --- Authorization (OAuth2) ---
# Step 1
def get_code_verifier():
    """Generates a code verifier with the length of 128.
    Google "AOuth 2 simplified" to learn about "code verifier".
    """
    token = token_urlsafe(100)
    return token[:128]

# Step 2
def print_auth_link(code_verifier):
    url = f'https://myanimelist.net/v1/oauth2/authorize?response_type=code&client_id={CLIENT_ID}&code_challenge={code_verifier}'
    print("Authorize application by going to the following link: \n", url, '\n')

# Step 3
def get_acc_token(code_verifier, auth_code):
    """
    Uses code verifier and authorization code obtained in the
    previous two steps to get access token from the service.

    On succesful execution, this will return a dictionary
    that will contain access token and some additional data.
    """
    url = 'https://myanimelist.net/v1/oauth2/token'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {
        'client_id': CLIENT_ID,
        'code': auth_code,
        'code_verifier': code_verifier,
        'grant_type': 'authorization_code'
    }
    res = requests.post(url, data=payload, headers=headers, timeout=2)
    res.raise_for_status()
    token = res.json()
    
    return token

# Step 4
def save_tokens(username: str, new_data: dict):
    """Saves tokens to mal_token.json file.
    Creates the file if it does'nt exist.
    
    JSONDecodeError is used to deal with empty file.
    """
    try:
        with open('mal_tokens.json', 'r+') as f:
            users_data = json.load(f)
            users_data[username] = dict()
            users_data[username].update(new_data)
            f.seek(0)
            json.dump(users_data, f, indent=4)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        with open('mal_tokens.json', 'w') as f:
            users_data = dict()
            users_data[username] = dict()
            users_data[username].update(new_data)
            json.dump(users_data, f, indent=4)

# Step 1-4
def main_auth(username):
    """
    Combines all authorization steps into one function,
    call this function to authorize user.

    username argument is passed to save_tokens function. 
    """
    code_verifier = code_challange = get_code_verifier()
    print_auth_link(code_verifier)
    auth_code = input("Copy-Paste the code here: ").strip()
    tokens = get_acc_token(code_verifier, auth_code)
    save_tokens(username, tokens)
    print("Authorized.")

def refresh_token(refresh_token, username):
    """Refresh tokens and save new tokens to file."""
    url = 'https://myanimelist.net/v1/oauth2/token'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {
        'client_id': CLIENT_ID,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    res = requests.post(url, data=payload, headers=headers, timeout=2)
    print(res)
    
    new_tokens = res.json()
    save_tokens(username, new_tokens)

    print('Tokens refreshed!')


# --- API Endpoints ---
# NOTE: You have to call load_token() before
#       calling most functions in this section.
def get_anime_list(search, limit=5, offset=None):
    endpoint = 'https://api.myanimelist.net/v2/anime'
    headers = {'X-MAL-CLIENT-ID': CLIENT_ID}
    params = {'q': search, 'limit': limit, 'offset': offset}

    res = requests.get(endpoint, params=params, headers=headers, timeout=2)
    print_response(res)

def get_user_info(access_token, fields=None):
    endpoint = 'https://api.myanimelist.net/v2/users/@me'
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {'fields': fields}
    
    res = requests.get(endpoint, params=params, headers=headers, timeout=2)
    print_response(res)

def update_eps(access_token, anime_id, num_watched_eps):
    endpoint = f'https://api.myanimelist.net/v2/anime/{int(anime_id)}/my_list_status'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Bearer {access_token}'
        }
    payload = {'num_watched_episodes': int(num_watched_eps)}
    
    res = requests.patch(endpoint, data=payload, headers=headers, timeout=2)
    print_response(res)

def get_user_anime_list(access_token):
    endpoint = 'https://api.myanimelist.net/v2/users/@me/animelist'
    headers = {'Authorization': f'Bearer {access_token}'}
    
    res = requests.get(endpoint, headers=headers, timeout=2)
    print_response(res)


# --- Complementary Functions ---
def load_token(username):
    """Returns user's tokens if found.
    Returns "not_found" if user is not registered,
    or if file does not exist, or is empty.

    JSONDecoderError is used to deal with empty file. 
    """
    return_val = None
    try:
        with open('mal_tokens.json', 'r') as f:
            users_data = json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        print(f"No tokens found for {username}.")
        return_val = 'not_found'
    else:
        if username in users_data.keys():
            user_tokens = users_data[username]
            return_val = user_tokens
            print("Token loaded.")
        else:
            print(f"No tokens found for {username}.")
            return_val = 'not_found'

    return return_val

def help_msg():
    msg = """
        Commands        Discription : Syntax

               q        Quit application
               h        Display this message
            auth        Authorize application
          ld tkn        Load user's token from data file
          rf tkn        Refresh tokens (and save new tokens to file)
           p tkn        Print user's tokens

          gt inf        Get user info : gt inf -[field]
          up eps        Update episode : up eps -[anime id] -[episode number]
          gt lst        Get user's anime list
              sr        Search anime : sr -[search] -[fields]
    """
    print(msg)

def handle_input(user_input):
    """Call different functions based on user input."""
    global tokens
    cmd, *args = user_input.split(' -')
 
    if cmd == 'q':
        sys.exit(0)
    elif cmd == 'h':
        help_msg()
    elif cmd == 'auth':
        main_auth(username)
    elif cmd == 'ld tkn':
        tokens = load_token(username)
    elif cmd == 'rf tkn':
        refresh_token(tokens['refresh_token'], username)
    elif cmd == 'p tkn':
        pprint(tokens)
    elif cmd == 'gt inf':
        get_user_info(tokens['access_token'], *args)
    elif cmd == 'up eps':
        update_eps(tokens['access_token'], *args)
    elif cmd == 'gt lst':
        get_user_anime_list(tokens['access_token'])
    elif cmd == 'sr':
        get_anime_list(*args)
    else:
        print("Command not recognized!")

def print_response(res):
    print(res)

    print("Response in text: ")
    print(res.text)
    
    print("\nResponse in JSON: ")
    pprint(res.json())


# --- Main Loop ---
def main_mal():
    global username, tokens
    username = input('Enter your username: ')
    tokens = {'access_token': 'Token not loaded.'}
    help_msg()

    running = True
    while running:
        user_input = input('\n--> ').strip()
        
        try:
            handle_input(user_input)
        except Exception as err:
            print('An error occurred:\n', err)

if __name__ == "__main__":
    main_mal()
