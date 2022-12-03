# MyAnimeList & Anilist Clients
A barebone MyAnimeLIst & Anilist clients written in python.

### Instructions
1. Run the script from command line.  
2. Enter a username.  
3. Enter `auth` to authorize application.  
4. Enter `ld tkn` to load tokens.  
5. Enter `h` for help message.  

You only need to use `auth` the first time running the script.  

By default MAL API doesn't return all fields. You can choose the fields  
that you want returned with the `fields` parameter. To pass a fields parameter 
to a command, prepend it with dash. ex: `gt inf -anime_statistics`.  
Different endpoints have different valid values for the `fields` parameter.  
Check out the [official docs](https://myanimelist.net/apiconfig/references/api/v2) for more information.

