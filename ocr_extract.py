import cv2
import easyocr
import math


class VideoFrameExtractor:

    def __init__(self, video_path):
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.reader = easyocr.Reader(['en'], gpu=True)

    def get_frame_pixels(self, frame_number):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = self.cap.read()
        if not ret:
            print(f"Cannot read frame {frame_number}")
            return None
        return frame

    def cut_frame(self, frame_number, y_start, y_end, x_start, x_end):
        frame = self.get_frame_pixels(frame_number)
        if frame is None:
            return None
        return frame[y_start:y_end, x_start:x_end]

    def preprocess_for_second_ocr(self, image, factor=1.2):
        if image is None or image.size == 0:
            return None
        upscaled = cv2.resize(image, None, fx=factor, fy=factor, interpolation=cv2.INTER_LANCZOS4)
        return upscaled

    def get_numbers_from_image(self, image, allowlist="0123456789."):
        if image is None or image.size == 0:
            return [], []

        results = self.reader.readtext(
            image,
            allowlist=allowlist,
            detail=1,
            paragraph=False
        )

        numbers = []
        confidences = []

        for (_, text, conf) in results:
            if not text:
                continue

            clean_text = text.strip().replace(" ", "")

            if clean_text:
                numbers.append(clean_text)
                confidences.append(float(conf))

        return numbers, confidences

    def double_ocr(self, roi, allowlist="0123456789", factors=[1.0, 1.1, 1.2, 1.3, 1.5], needed_occurrences=4):
        results = []

        for factor in factors:
            processed = self.preprocess_for_second_ocr(roi, factor=factor)
            numbers, confs = self.get_numbers_from_image(processed, allowlist=allowlist)

            if numbers:
                results.append((tuple(numbers), confs))  

        if len(results) < needed_occurrences:
            return None, None

        counts = {}
        for numbers, confs in results:
            if numbers not in counts:
                counts[numbers] = []
            counts[numbers].append(confs)

        for numbers, conf_lists in counts.items():
            if len(conf_lists) >= needed_occurrences:
                avg_confs = []
                for i in range(len(conf_lists[0])):
                    vals = [confs[i] for confs in conf_lists]
                    avg_confs.append(sum(vals) / len(vals))
                return list(numbers), avg_confs

        return None, None

    def save_frame(self, frame_array, output_path):
        if frame_array is not None:
            cv2.imwrite(output_path, frame_array)
        else:
            print("No valid frame to save.")

    def deinit(self):
        self.cap.release()


def calculate_distance(lat1, lon1, lat2, lon2):
    lat_diff = abs(lat2 - lat1)
    lon_diff = abs(lon2 - lon1)
    distance = math.sqrt(lat_diff**2 + lon_diff**2)
    return distance


def retrieve_data_from_video2(video_path, output_path="output/output.csv"):
    extractor = VideoFrameExtractor(video_path)
    frame_number = 0
    conf_threshold = 0.8

    all_data = []
    last_valid_location = None
    previous_altitude = 0.0

    while True:
        ret, frame = extractor.cap.read()
        frame_number += 1
        if not ret:
            break

        roi = frame[45:140, 50:415]
        altitude_roi = frame[140:180, 50:190]

        # doble OCR – returns results only if both OCRs match
        numbers, confs = extractor.double_ocr(roi, allowlist="0123456789")

        numbers_alt, confs_alt = extractor.double_ocr(altitude_roi, allowlist="0123456789")

        if numbers is None:
            print(f"Frame {frame_number}: Difference between OCR's, skipping.")
            continue

        if len(numbers) == 2:
            LAT, LON = numbers
            LAT_conf, LON_conf = confs

            if not LAT.isdigit() or not LON.isdigit():
                continue

            if LAT_conf < conf_threshold and LON_conf < conf_threshold:
                print(
                    f"Frame {frame_number}: low confidence (LAT_conf={LAT_conf:.2f}, LON_conf={LON_conf:.2f}),{LAT}, {LON}, Skipping."
                )
            else:
                true_LAT = float(LAT[:2] + '.' + LAT[2:])
                true_LON = float(LON[:2] + '.' + LON[2:])
                true_ALT = previous_altitude
                if numbers_alt and confs_alt and confs_alt[0] >= conf_threshold:
                    true_ALT = float(numbers_alt[0])
                    previous_altitude = true_ALT

                print(f"Frame {frame_number}: {true_LAT}, {true_LON}, {true_ALT}")
                all_data.append(f"{true_LAT},{true_LON},{true_ALT}")
                last_valid_location = (true_LAT, true_LON)

        # End loop if we reach 12000 frames to avoid infinite processing
        if frame_number >= 12000:
            break
    # save date to CSV
    with open(output_path, "w", encoding="utf-8") as f:
        for row in all_data:
            f.write(row + "\n")
    print(f"Data saved to {output_path}")
    extractor.deinit()


if __name__ == "__main__":
    video_path = "VID00001.avi"
    retrieve_data_from_video2(video_path)
