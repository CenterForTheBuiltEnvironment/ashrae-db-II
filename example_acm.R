#### ADAPTIVE COMFORT MODEL 2 ###
# example analysis of adaptive comfort modified after 10.1016/j.enbuild.2019.109559
# written by Thomas Parkinson, May 2022
# NOTE: please consider citing 10.1016/j.enbuild.2019.109559 if you found this script useful in your own work



#### SETUP ####

# load packages
library(tidyverse)
library(broom)
library(ggpmisc)
library(scales)



#### DATA PREPARATION ####

# read in metadata from Github as data table
df_meta <- read_csv("https://github.com/CenterForTheBuiltEnvironment/ashrae-db-II/raw/master/v2.1.0/db_metadata.csv")

# plot map of data records
df_meta %>%
  group_by(country) %>%
  summarise(records = sum(records, na.rm = TRUE)) %>%
  ungroup() %>%
  mutate(country = str_to_title(country),
         country = str_replace(country, "Usa", "USA"),
         country = str_replace(country, "Uk", "UK")) %>%
  left_join(map_data("world"), ., by = c("region" = "country")) %>%
  ggplot(., aes(x = long, y = lat)) +
  geom_polygon(aes(fill = records, group = group), colour = "grey95", size = 0.3) +
  geom_point(data = distinct(df_meta, lon, lat), aes(x = lon, y = lat), 
             size = 1.5, shape = 16, colour = "#52489C", alpha = 0.6) +
  scale_fill_gradient(low = '#D1D6F0', high = "#465BC3", na.value = "grey90") +
  labs(title = "ASHRAE Global Thermal Comfort Database II",
       subtitle = "Records by country in version 2.1 of the database",
       x = NULL, y = NULL) +
  guides(fill = "none") +
  coord_fixed(ratio = 1, xlim = NULL, ylim = c(-50, 90), expand = TRUE, clip = "on") +
  theme_void() +
  theme(plot.title = element_text(hjust = 0.5, size = 14, face = "bold", colour = "grey20"),
        plot.subtitle = element_text(hjust = 0.5, size = 12, face = "italic", colour = "grey40"),
        panel.grid.minor = element_blank(),
        panel.grid.major.x = element_blank(),
        panel.background = element_blank(),
        panel.border = element_blank(),
        axis.ticks = element_blank(),
        axis.text = element_blank(),
        plot.margin = margin(0.1, 0.4, 0.1, 0.4, "cm"))

# save map
ggsave(file = "database_map.png", width = 7, height = 2.8, dpi = 300)


# read in database from Github as data table
df_measurements <- read_csv("https://github.com/CenterForTheBuiltEnvironment/ashrae-db-II/raw/master/v2.1.0/db_measurements_v2.1.0.csv.gz")

# subset records with indoor air temperature, thermal sensation, relative humidity, and meteorological data
df_acm2 <- df_measurements %>%
  filter(!is.na(ta) & 
           !is.na(thermal_sensation) & 
           !is.na(rh) & 
           (!is.na(t_out_isd)|!is.na(t_out)))

# collapse outdoor met data
df_acm2 <- df_acm2 %>%
  mutate(t_out_combined = case_when(!is.na(t_out_isd) ~ t_out_isd,
                                    is.na(t_out_isd) & !is.na(t_out) ~ t_out,
                                    TRUE ~ NA_real_)) %>%
  select(-c(t_out_isd, t_out))

# add relevant parameters from metadata table
df_acm2 <- df_meta %>%
  select(building_id, region, building_type, cooling_type, records) %>%
  left_join(df_acm2, ., by = "building_id")

# subset records from office buildings only
df_acm2 <- df_acm2 %>%
  filter(building_type == "office") %>%
  select(-building_type)



#### ADAPTIVE COMFORT ANALYSIS ####

# do linear models for each building id
df_models <- df_acm2 %>%
  nest(data = -c(building_id)) %>%
  mutate(fit = map(data, ~ lm(thermal_sensation ~ ta, data = .x)),
         tidy = map(fit, broom::tidy))

# get model coefficients
df_models <- df_models %>%
  select(building_id, tidy) %>%
  unnest(tidy, names_sep = "_") %>%
  arrange(building_id)

# drop insignificant models and keep neutral temperatures
df_models <- df_models %>%
  filter(tidy_term == "(ta)", 
         tidy_p.value < 0.05) %>%
  select(building_id,
         "neutral_temp" = "tidy_estimate")

# add in sample size
df_models <- df_meta %>%
  select(building_id, records, cooling_type, region) %>%
  left_join(df_models, ., by = "building_id")

# add mean outdoor temperature
df_models <- df_acm2 %>%
  group_by(building_id) %>%
  summarise(t_out_mean = mean(t_out_combined)) %>%
  ungroup() %>%
  left_join(df_models, ., by = "building_id")



#### VISUALIZATION ####

# plot adaptive comfort model
df_models %>%
  filter(t_out_mean >= 10 & t_out_mean <= 33, # remove data beyond limits
         neutral_temp > 17 & neutral_temp < 32) %>% # remove outliers
  mutate(cooling_type = str_to_title(cooling_type)) %>%
  ggplot(., aes(x = t_out_mean, y = neutral_temp, colour = cooling_type)) +
  annotate("segment", x = c(10, 10, 10, 10, 10), xend = c(33.5, 33.5, 33.5, 33.5, 33.5),
          y = c(17.4, 18.4, 20.9, 23.4, 24.4), yend = c(24.5, 25.5, 28.0, 30.5, 31.5),
          linetype = c("solid", "dashed", "dotted", "dashed", "solid"),
          color = "grey30", size = 0.3) +
  geom_point(aes(size = records), shape = 16, alpha = 0.25) +
  geom_smooth(aes(fill = cooling_type, weight = records), method = lm, se = TRUE, alpha = 0.1) + 
  #stat_poly_eq(formula = y ~ x, aes(label = paste(..eq.label.., ..rr.label.., sep = "~~~")), eq.x.rhs = "t_out",
  #             label.x = 0.09, parse = TRUE, size = 2.5, vstep = 0.035) +
  scale_x_continuous(expand = c(0, 0), breaks = seq(10, 30, by = 5), 
                     labels = number_format(accuracy = 1L, suffix = "°C")) +
  scale_y_continuous(expand = c(0, 0), breaks = seq(20, 30, by = 5),
                     labels = number_format(accuracy = 1L, suffix = "°C")) +
  scale_color_manual(values = c("Air Conditioned" = "#000000", 
                                "Mixed Mode" = "#E69F00", 
                                "Naturally Ventilated" = "#56B4E9")) +
  scale_fill_manual(values = c("Air Conditioned" = "#000000", 
                                "Mixed Mode" = "#E69F00", 
                                "Naturally Ventilated" = "#56B4E9")) +
  annotate("text", x = c(33.7, 33.7, 33.7, 33.7, 33.7), y = c(24.5, 25.5, 28.0, 30.5, 31.5),
          label = c("Lower 80%", "Lower 90%", "", "Upper 90%", "Upper 80%"),
          color = "grey30", fontface = "italic", hjust = 0, vjust = 0.5, size = 2.5) +
  labs(title = "Adaptive Comfort Model",
       subtitle = "Example analysis of adaptive thermal comfort using the ASHRAE Global Thermal Comfort Database II",
       caption = "Adapted from https://doi.org/10.1016/j.enbuild.2019.109559",
       x = "\nOutdoor Temperature", y = "Neutral Temperature\n", color = NULL) +
  guides(color = guide_legend(override.aes = list(fill = NA, label.position = "bottom")), 
         size = "none", fill = "none", alpha = "none") +
  coord_cartesian(clip = "off", xlim = c(8, 32), ylim = c(17, 33)) +
  theme_minimal(base_size = 10) +
  theme(plot.title = element_text(size = 14, colour = "grey20", face = "bold", hjust = 0.5),
        plot.subtitle = element_text(size = 10, colour = "grey20", face = "italic", hjust = 0.5, margin = margin(b = 10)),
        plot.caption = element_text(size = 6, colour = "grey20", face = "italic", hjust = 0.5),
        panel.grid.minor = element_blank(),
        panel.grid.major = element_line(size = 0.25, colour = "grey90"),
        legend.position = "top",
        plot.background = element_rect(fill = "white"),
        plot.margin = margin(2, 30, 2, 2, unit = "mm"))

# save plot
ggsave(file = "acm2_plot.png", width = 8, height = 5, dpi = 300)


#### END
