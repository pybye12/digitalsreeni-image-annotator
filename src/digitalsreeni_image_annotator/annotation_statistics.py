import plotly.graph_objects as go
from plotly.subplots import make_subplots
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextBrowser, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt
import tempfile
import os
import webbrowser


def summarize_annotations(annotations):
    """Summarize frame annotations and unique tracked droplet events."""
    class_distribution = {}
    objects_per_image = {}
    total_objects = 0
    droplet_event_ids = set()
    droplet_frame_annotations = 0

    for image, image_annotations in annotations.items():
        objects_in_image = 0
        for class_name, class_annotations in image_annotations.items():
            class_count = len(class_annotations)
            class_distribution[class_name] = (
                class_distribution.get(class_name, 0) + class_count
            )
            objects_in_image += class_count
            total_objects += class_count
            if class_name == "droplet":
                droplet_frame_annotations += class_count
                for annotation in class_annotations:
                    event_id = annotation.get("droplet_event_id") or annotation.get(
                        "sam3_source_id"
                    )
                    if event_id:
                        droplet_event_ids.add(event_id)
        objects_per_image[image] = objects_in_image

    return {
        "class_distribution": class_distribution,
        "objects_per_image": objects_per_image,
        "total_objects": total_objects,
        "droplet_frame_annotations": droplet_frame_annotations,
        "unique_droplet_events": len(droplet_event_ids),
    }


class AnnotationStatisticsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Annotation Statistics")
        self.setGeometry(100, 100, 600, 400)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.Window)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.text_browser = QTextBrowser()
        layout.addWidget(self.text_browser)

        button_layout = QHBoxLayout()
        self.show_plot_button = QPushButton("Show Interactive Plot")
        self.show_plot_button.clicked.connect(self.show_interactive_plot)
        button_layout.addWidget(self.show_plot_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.plot_file = None

    def show_centered(self, parent):
        parent_geo = parent.geometry()
        self.move(parent_geo.center() - self.rect().center())
        self.show()

    def generate_statistics(self, annotations):
        try:
            summary = summarize_annotations(annotations)
            class_distribution = summary["class_distribution"]
            objects_per_image = summary["objects_per_image"]
            total_objects = summary["total_objects"]
    
            avg_objects_per_image = total_objects / len(annotations) if annotations else 0
    
            # Create plots
            fig = make_subplots(rows=2, cols=1, subplot_titles=("Class Distribution", "Objects per Image"))
    
            # Class distribution plot
            fig.add_trace(go.Bar(x=list(class_distribution.keys()), y=list(class_distribution.values()), name="Classes"),
                          row=1, col=1)
    
            # Objects per image plot
            fig.add_trace(go.Bar(
                x=list(objects_per_image.keys()),
                y=list(objects_per_image.values()),
                name="Images",
                hovertext=[f"{img}: {count}" for img, count in objects_per_image.items()],
                hoverinfo="text"
            ), row=2, col=1)
    
            # Update layout
            fig.update_layout(height=800, title_text="Annotation Statistics")
            
            # Hide x-axis labels for the second subplot (Objects per Image)
            fig.update_xaxes(showticklabels=False, title_text="Images", row=2, col=1)
            
            # Update y-axis title for the second subplot
            fig.update_yaxes(title_text="Number of Objects", row=2, col=1)
    
            # Save the plot to a temporary HTML file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as tmp:
                fig.write_html(tmp.name)
                self.plot_file = tmp.name
    
            # Display statistics in the text browser
            stats_text = f"Total objects: {total_objects}\n"
            stats_text += f"Average objects per image: {avg_objects_per_image:.2f}\n\n"
            stats_text += (
                f"Unique tracked droplet events: "
                f"{summary['unique_droplet_events']}\n"
            )
            stats_text += (
                f"Droplet frame annotations: "
                f"{summary['droplet_frame_annotations']}\n\n"
            )
            stats_text += "Class distribution:\n"
            for class_name, count in class_distribution.items():
                stats_text += f"  {class_name}: {count}\n"
    
            self.text_browser.setPlainText(stats_text)
    
        except Exception as e:
            self.text_browser.setPlainText(f"An error occurred while generating statistics: {str(e)}")
            self.show_plot_button.setEnabled(False)

    def show_interactive_plot(self):
        if self.plot_file and os.path.exists(self.plot_file):
            webbrowser.open('file://' + os.path.realpath(self.plot_file))
        else:
            self.text_browser.append("Error: Plot file not found.")

    def closeEvent(self, event):
        if self.plot_file and os.path.exists(self.plot_file):
            os.unlink(self.plot_file)
        super().closeEvent(event)

def show_annotation_statistics(parent, annotations):
    dialog = AnnotationStatisticsDialog(parent)
    dialog.generate_statistics(annotations)
    dialog.show_centered(parent)
    return dialog
