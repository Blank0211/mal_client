import sys, json, secrets, pprint
import requests
CLIENT_ID = "d2b59caf73a52c2d8c6a5be3e7bd9733"


# --- Authorization (OAuth2) ---
# Step 1
def get_code_verifier():
    """Generates a code verifier with the length of 128.
    Google "AOuth 2 simplified" to learn about "code verifier".
    """
    token = secrets.token_urlsafe(100)
    return token[:128]

# Step 2
def print_auth_link(code_verifier):
    url = f'https://myanimelist.net/v1/oauth2/authorize?response_type=code&client_id={CLIENT_ID}&code_challenge={code_verifier}'
    print("Authorize the app by going to the following link: \n", url, '\n')

# Step 3
def get_acc_token(code_verifier, auth_code):
    """
    Uses code verifier and authorization code obtained in the
    previous two steps to get access token from the service.

    On succesful execution, this will return a dictionary
    that will contain access token and some additional data.
    """
    url = 'https://myanimelist.net/v1/oauth2/token'
    payload = {
        'client_id': CLIENT_ID,
        'code': auth_code,
        'code_verifier': code_verifier,
        'grant_type': 'authorization_code'
    }
    res = requests.post(url, data=payload, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    res.raise_for_status()

    token = res.json()
    print(token, res.text, type(res.text), res.status_code, sep='\n')

    return token

# Step 4
def save_tokens(username: str, new_data: dict):
    """Save the tokens to mal_token.json file.
    If file does not exist, this will create it.
    
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


# --- Commands ---
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
            print("You are logged in.")
        else:
            print(f"No tokens found for {username}.")
            return_val = 'not_found'

    return return_val

def help_msg():
    msg = """
        Commands        Discription

               q        Quit application
            auth        Authorize application
          ld tkn        Load user's token from data file 
           p tkn        Print user's tokens
    """
    print(msg)


# --- Main ---
def main():
    username = input('Enter your MAL username: ')
    user_token = 'Token not loaded. Use <ld tok> to load token'

    running = True
    while running:
        command = input('--> ')
        if command == 'q':
            break
        elif command == '-help':
            help_msg()
        elif command == 'auth':
            main_auth(username)
        elif command == 'ld tkn':
            user_token = load_token(username)
        elif command == 'p tkn':
            pprint.pprint(user_token)
        else:
            print("Command not recognized!")

if __name__ == "__main__":
    main()
