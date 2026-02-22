import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np


def load_data_from_csv(csv_path):
    data = []
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    lat, lon, altitude = map(float, line.split(","))
                    data.append((lat, lon, altitude))
    except FileNotFoundError:
        print(f"Plik {csv_path} Not found!")
        return []
    
    print(f"Loaded {len(data)} points from {csv_path}")
    return data


def visualize_2d_data(data, draw_indexes=True):
    if not data:
        print("No data to visualize!")
        return
    
    lats = [c[0] for c in data]
    lons = [c[1] for c in data]

    plt.figure(figsize=(10, 8))
    plt.plot(lons, lats, 'b-', alpha=0.5, label="Path")
    plt.scatter(lons, lats, c='red', s=20, label="Points")
    
    if draw_indexes:
        for i, (lon, lat) in enumerate(zip(lons, lats)):
            plt.text(lon, lat, str(i), fontsize=6, ha='center', va='bottom', alpha=0.7)
    
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.title("Geo points (2D)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.axis("equal")
    plt.show()


def visualize_3d_data(data, draw_indexes=True):
    if not data:
        print("No data to visualize!")
        return
    
    lats = [c[0] for c in data]
    lons = [c[1] for c in data]
    altitudes = [c[2] for c in data]

    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111, projection='3d')
    
    ax.plot(lons, lats, altitudes, 'b-', alpha=0.5, label="Path")
    ax.scatter(lons, lats, altitudes, c='red', s=20, label="Points")
    
    if draw_indexes:
        for i, (lon, lat, alt) in enumerate(zip(lons, lats, altitudes)):
            ax.text(lon, lat, alt, str(i), fontsize=8, ha='center', va='bottom', alpha=0.7)
    
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_zlabel("Altitude (m)")
    ax.set_title("Geo points (3D)")
    ax.legend()
    plt.show()


def save_data_to_csv(data, output_path):
    if not data:
        print("No data to save!")
        return
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            for lat, lon, altitude in data:
                f.write(f"{lon},{lat},{altitude}\n")
        print(f"Saved {len(data)} points to file {output_path}")
    except Exception as e:
        print(f"Error while saving file: {e}")


if __name__ == "__main__":
    csv_path = "output/output.csv"
    data = load_data_from_csv(csv_path)
        
    print("\n--- Show 2D plot ---")
    visualize_2d_data(data, draw_indexes=True)

    print("\n--- Show 3D plot ---")
    visualize_3d_data(data, draw_indexes=True)
    
    print("\n--- Save data to file ---")
    save_data_to_csv(data, "output/output_revert.csv")
