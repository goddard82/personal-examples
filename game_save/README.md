# game save project

I want to explore creating a save file that would work across platforms/devices. I recently played a game with my son
and discovered that our save would not be compatible when we upgrade to the next gen version.

In a Game As A Service, the player save data is understandably stored in the cloud. For example, a Postgres DB hosted on
AWS infra.

Imagine a console game, that saves locally but can also upload the save to the console-specific cloud data service. Now
imagine you want to continue playing the same game, but on a next-gen system. Is the save compatible? _Could_ it be?

"Super Fun Social Game" is a GaaS mobile title, with millions of players. The game is pretty simple - players create an
Avatar that has various outfit and inventory slots, and an in-game inbox.

These items are retrieved when the player logs in, even on a new device.

This same logic should be implementable in console games.

## How

"Open world exploration title" is a 3D open world survival game.

An "outfit" save file *might* look like this:

```{
	"uuid": "4042b1be-f946-4db8-abac-8aebc66cc10f",
	"type": "outfit",
	"data": {
		"animationdetails": [],
		"gender": "female01",
		"headscale": 1,
		"slots": 5,
		"itemdetails": [
			{
				"colour": "109, 57, 43, 255",
				"details": "(0.000,0.000,0.000,0.000)",
				"filename": "eyebrows_017",
				"id": "d1126e26e8d",
				"key": "trousers"
			},
			{
				"colour": "109, 57, 43, 255",
				"details": "(0.000,0.000,0.000,0.000)",
				"filename": "eyebrows_017",
				"id": "d1126e26e8d",
				"key": "feet"
			},
			{
				"colour": "109, 57, 43, 255",
				"details": "(0.000,0.000,0.000,0.000)",
				"filename": "eyebrows_017",
				"id": "d1126e26e8d",
				"key": "jacket"
			},
			{
				"colour": "154, 119, 100, 255",
				"details": "(0.000,0.000,0.000,0.000)",
				"filename": "eyes_019",
				"id": "YTu9Ysbep3eVKrw7",
				"key": "helmet"
			},
			{
				"colour": "154, 119, 100, 255",
				"details": "(0.000,0.000,0.000,0.000)",
				"filename": "eyes_019",
				"id": "YTu9Ysbep3eVKrw7",
				"key": "back"
			}
		],
		"name": "OpenWorldExplorationTitle",
		"oldid": 0,
		"uuid": "4042b1be-f946-4db8-abac-8aebc66cc10f",
		"version": "1.16"
	},
	"date": 1645095311
}
```

This would be retrieved via an http endpoint in the GaaS title, and be JWT encoded (or similar.)

For a console title, this and other save files could be similarly stored and retrieved, as long as the API that serves
them is secure.

### Console implementation

Let's say that "Open world exploration title" has the usual open world stuff:

- story missions
- side quests
- watchtowers/similar map progression mechanic
- collectibles
- upgrades
- stats (think 'bears killed', 'rounds fired', 'days in game', etc)
  A save file containing all of these things should be transferrable to a next gen console or other platform, right?

Even seemingly advanced or difficult things to save & transfer, such as building damage, random encounters, a heat map
of where the player has been, could all be recorded.

There could be a number of save configs, but here's a rough example of a progression save file:

```
{
	"uuid": "202b1be-f946-4db8-abac-8aebc66cc10f",
	"type": "progression",
	"data": {
		"tutorials": [
			{
				"id": "mvm1",
				"complete": true
			},
			{
				"id": "gun1",
				"complete": true
			},
			{
				"id": "turn",
				"complete": false
			}
		],
		"missions": [
			{
				"id": "d1045d",
				"state": "passed",
				"stats": {
					"progstatafter": 11.15,
					"attempts": 1,
					"kills": {
						"henchman1": {
							"killedby": "headshot"
						},
						"henchman2": false,
						"henchman3": {
							"killedby": "headshot"
						}
					}
				}
			}
		],
		"collectibles": [
			{
				"id": "p1",
				"state": "collected",
				"ts": 1645099024
			},
			{
				"id": "p16",
				"state": "collected",
				"ts": 1645099359
			}
		],
		"unlocks": [
			{
				"weapons": [
					{
						"colour": "109, 57, 43, 255",
						"details": "(0.000,0.000,0.000,0.000)",
						"filename": "stasisrifle",
						"id": "d1126e26e8d"
					},
					{
						"colour": "109, 57, 43, 255",
						"details": "(0.000,0.000,0.000,0.000)",
						"filename": "brassknuckles1",
						"id": "wbkn1"
					}
				],
				"hats": [
					{
						"filename": "trilby7",
						"id": "d1126e26e8d"
					},
					{
						"filename": "porkpie",
						"id": "YTu9Ysbep3eVKrw7"
					}
				]
			}
		],
		"name": "OpenWorldExplorationTitle",
		"currentprogressionpercentage": 11.15,
		"version": "1.16"
	},
	"retrieveddate": 1645099024
}
```


## Further thinking

Even a JWT (or otherwise) encoded json config is exploitable by hackers/modders. Any endpoints that facilitate the
transfer of player data should be protected. They will be found, and players will attempt to gain an unfair advantage
through aquiring items they don't own, etc. Validation will be required in the API (i.e - "is the item in the POST request to the "edit back slot" endpoint of type 'back'?")

It may be good practise to store the saves on the console and periodically save/load the cloud versions.

It would be possible to create an item viewer for internal testing using some of the same code here.
