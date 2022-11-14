# MyAnimeList Client (Python)
A barebone python CLI application to work with MAL's API.

### Instructions
Run the script from command line and enter a username. enter "h" to get the list of 
commands and their discription

By default MAL API doesn't return all fields. You can choose the fields  
that you want returned with the `fields` parameter. To pass a fields parameter 
to a command, prepend it with dash. ex: `gt inf -anime_statistics`.  
Different endpoints have different valid values for the `fields` parameter.  
Check out the [official docs](https://myanimelist.net/apiconfig/references/api/v2) for more information.

