# Configure the CRAN mirror
options(repos = c(CRAN = "https://cloud.r-project.org"))


# Install required packages if they are not already installed
if (!requireNamespace("readr", quietly = TRUE)) {
  install.packages("readr")
}
if (!requireNamespace("ggplot2", quietly = TRUE)) {
  install.packages("ggplot2")
}

library(readr)
library(ggplot2)

# Path to the CSV file
csv_path <- "../database/sensor_data.csv"

# Load the sensor data from the CSV file
sensor_data <- read_csv(csv_path)

# Create a basic scatter plot for humidity vs temperature
p <- ggplot(sensor_data, aes(x = humidity, y = temperature)) +
  geom_point(color = "blue") +
  labs(
    title = "Relation between Humidity and Temperature",
    x = "Humidity (%)",
    y = "Temperature (°C)"
  )

# Save the plot as a PNG file
ggsave("outputs/r_plot.png", plot = p, width = 6, height = 4)

# Generate a statistical summary of the data
summary_stats <- summary(sensor_data)

# Save the summary to a text file
write(summary_stats, file = "outputs/summary.txt")

# Print the summary to the console
print(summary_stats)
