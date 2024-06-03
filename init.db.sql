CREATE TABLE IF NOT EXISTS wishlist (
    id SERIAL PRIMARY KEY,
    destination VARCHAR(20),
    planned_date DATE,
    weather_forecast VARCHAR(200),
    recommendation VARCHAR(200)
);