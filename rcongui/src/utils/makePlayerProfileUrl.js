const makePlayerProfileUrl = (playerId, name = "") => {
  if (playerId.length === 17) {
    // valid steam id is 17 digits...
    return `https://steamcommunity.com/profiles/${playerId}`;
  } else if (name.length > 0) {
    // xbox gamertags are unique and cost $$ to change...
    // otherwise assume it's a T17 guid and return
    // a url to https://xboxgamertag.com/search/ name
    return `https://xboxgamertag.com/search/${name}`;
  }
};

export default makePlayerProfileUrl;
