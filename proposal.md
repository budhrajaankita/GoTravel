## Team name & Team members
- Name: GoTravel
- Members: Dhanya Koottummel, Ankita Budhraja, Hrishikesh Nagaraju, Wenjing Lin, Xu Cheng

## Project ideas
The API we want to build is called *“GoTravel”*, which helps users plan their trips by providing information on their desired destinations, and allow users to maintain their travel wishlist. Specifically, users can check and modify their own wishlist, and the corresponding data will be persisted in a PostgreSQL database. 

Here is an outline of the API endpoints, functionality, and possible external APIs included:
- `/recommend` - GET - chatgpt API - provides users with the information on their desired destinations 
- `/add` - POST - OpenWeatherMap API - allows users to add new destinations to their travel wishlist, and provide the weather of that location using OpenWeatherMap API
- `/favorites` - GET - endpoint for users to check their current wishlist
- `/edit` - PUT - users can modify the existing records in their wishlists
- `/delete` - DELETE - users can delete one or more records in their wishlists

## Expected external APIs
`OpenWeatherMap API`: provides a wide range of weather information such as temperature, humidity, wind speed, etc. This can be useful for people planning a trip, or simply curious about the weather conditions in a specific location. 

`ChatGPT API`: provides a more personalized and unique experience by generating an interesting fact about the location. This can be helpful for people who are researching a location for a trip, or simply want to learn something new about the place they are interested in.

Combining both the APIs will allow for a more engaging and informative experience for users who are interested in visiting a specific location. By providing both the weather information and an interesting fact about the location, users can gain a deeper understanding and appreciation for the place they are interested in.