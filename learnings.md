## Team name & your members

- Name: GoTravel (Group 9)
- Members: Dhanya Koottummel, Ankita Budhraja, Hrishikesh Nagaraju, Wenjing Lin, Xu Cheng

## What was your original goal and how much of it were you able to achieve?

Our project fulfills most of the original goals, but also subjects to some API limitations. For example:

- Time span for the weather forecast: limit to the free version of OpenWeather API
- Length of recommendations response: limit to the postgres string maximum length

## A description of what your project does and the functionality that it provides

- Our project helps users plan their trips by providing information on their desired destinations, and allow users to maintain their travel wishlist.
- Specifically, users are able to create and retrieve all the wishlist records. Also, for a particular wishlist, users can retrieve and modify (update / delete) its related information. More importantly, our project allows users to get weather forecasts and recommendations for the desired destination. It also provides the functionality to send your entire wishlist via email.

## What did you learn from the project? Talk about the mistakes you made, challenges you overcame or the tools that you got to learn etc

- More convenient and easy to collaborate starting with database
- Remember not to expose our API keys to github
- We also learned how to collaborate with a team using GitHub, especially when our tasks will most likely be intertwined and some parts might depend on others. So we learned to set realistic timelines for smooth collaboration and also merge our codes in a way that won’t cause conflicts such as using pull request for people to review before starting to work on the code
- We learnt more about OpenWeather API and chatGPT APIs. For many teammembers it was the first time using these APIs to build a project & we got a chance to see how the APIs work
- We also learnt about the limitations of using free versions of APIs. For example, OpenWeather API allows us to get weather data within the next 5 days only. Another challenge was that we had to convert the 'destination' to latitudes and longitude to get the appropriate weather data.
- Data format processing, e.g. date data in the OpenWeather API, response data in the ChatGPT API (sometimes string, sometimes list)
  Storage efficiency: Setting appropriate lengths for string columns helps you optimize storage usage. Allocating more space than needed can lead to wasted storage, while allocating too little space might truncate data or cause errors. This is a mistake that we made initially where we wanted a short description and set the ciolumn length accordingly & later had to update when we realized what we set was too short.
- Flexibility: Ensure that the column lengths are flexible enough to accommodate various data scenarios. For instance, the destination column might need to store longer city names, so consider increasing its length to avoid truncating data. Similarly, the weather_forecast and recommendation columns should have enough space to store detailed information
- Consistency with external data sources: When storing data fetched from external APIs, make sure column lengths are consistent with the data provided by those APIs. For example, if the OpenWeather API returns longer weather descriptions, we should adjust the weather_forecast column length accordingly
