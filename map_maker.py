import folium
from folium import plugins


def make_map(tankstellen):
    """Makes a folium map for the presentation with sufficiency markers and colors for our scenarios

    Args:
        tankstellen (gdf): File with sufficiency columns for each scenario

    Returns:
        None: saves map.html for hosting
    """
    m = folium.Map(
        location=[46.87, 8.3],
        tiles="openstreetmap",
        zoom_start=8,
    )

    def color_producer(suff):
        """Assigns colors of markers

        Args:
            suff (float): sufficiency of charging point

        Returns:
            String: String of color (must be css!)
        """
        if suff <= 0.8:
            return 'green'
        elif 0.8 <= suff <= 1:
            return 'lightgreen'
        elif 1 < suff < 1.5:
            return 'orange'
        elif 1.5 <= suff < 10:
            return "red"
        elif 10 <= suff < 100:
            return "purple"
        else:
            return "black"

    def populate_feature_group(sufficiency, feature_group):
        for i in range(len(tankstellen)):
            y = tankstellen['geometry'][i][0].x
            x = tankstellen['geometry'][i][0].y
            suff = tankstellen[sufficiency][i]
            folium.Marker([x, y], popup="Auslastung (eg. 0.5 => 50%): " + str(round(suff, 3)), icon=folium.Icon(
                color=color_producer(suff), icon="flash", icon_color='#FFFFFF')).add_to(feature_group)

    """ Make layer featuregroups for each scenario """
    tk_today = folium.FeatureGroup(name="Tankstellen Today")
    tk_b = folium.FeatureGroup(
        name="Tankstellen Business as usual", show=False)
    tk_z = folium.FeatureGroup(name="Tankstellen ZERO", show=False)
    tk_ze = folium.FeatureGroup(name="Tankstellen ZERO E", show=False)

    populate_feature_group("sufficiency_today", tk_today)
    populate_feature_group("sufficiency_BAU", tk_b)
    populate_feature_group("sufficiency_ZERO", tk_z)
    populate_feature_group("sufficiency_ZERO_E", tk_ze)

    # Make list of lat, long in wgs84 dec for heatmap
    x, y = [], []
    for i in range(len(tankstellen)):
        y.append(tankstellen['geometry'][i][0].x)
        x.append(tankstellen['geometry'][i][0].y)
    lat_long = list(zip(x, y))

    # Adding layers to map
    m.add_child(tk_today)
    m.add_child(tk_b)
    m.add_child(tk_z)
    m.add_child(tk_ze)
    plugins.HeatMap(lat_long).add_to(folium.FeatureGroup(
        name="Tankstellendichte", show=False).add_to(m))

    # Add Layer control
    m.add_child(folium.LayerControl())

    m.save("map.html")
