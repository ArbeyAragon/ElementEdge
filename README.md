### **README: ElementEdge Monitoring**

---

#### **Overview**
**ElementEdge Monitoring** is an advanced monitoring and visualization tool designed to aid in managing emergencies, monitoring vital signs, and providing real-time geolocated data for enhanced decision-making. The platform integrates IoT devices, interactive maps, AI, and chat functionality to deliver a comprehensive solution for both frontline workers and their administrators.

---

#### **Project Structure**

1. **`app.py`**:
   - The main application script for the **ElementEdge Monitoring** platform.
   - Built using **Dash**, **Dash Leaflet**, and **Dash Bootstrap Components**, this script provides:
     - **Interactive Map**:
       - Displays geolocated markers for fires, rescued individuals, and firefighters.
       - Real-time selection and interaction with markers to view details.
     - **Vital Sign Monitoring**:
       - Graphs for heart rate, oxygen level, temperature, and blood pressure, updated every second with simulated data.
     - **Video Feed**:
       - Integrates a real-time camera feed for additional situational awareness.
     - **Chat Functionality**:
       - Enables communication via a simulated chatbot interface.
     - **Dynamic Marker Interaction**:
       - Allows marker selection on the map, with icons dynamically updated to reflect selections.
   - Uses **OpenCV** to manage the video feed and **Plotly** for generating visualizations.

2. **`Architecture.svg`**:
   - High-level diagram illustrating the system's architecture.
   - Explains how data flows between hardware (sensors, cameras), software components (AI agents, Qualcomm RB3), and visualization layers (AR and dashboard).

3. **`AgentHierarchy.svg`**:
   - Displays the hierarchy and roles of AI agents, the manager, and the firefighter.
   - Highlights how agents handle tasks like medical support, danger assessment, and information sharing.

4. **`HardwareArchitecture.svg`**:
   - Explains the physical connections between components, including sensors (e.g., heart rate, oxygen), Arduino, Qualcomm RB3, cameras, microphones, and speakers.
   - Demonstrates how data is collected, processed, and relayed to the cloud or visualized on the map.

---

#### **How the Application Works**

1. **Data Input**:
   - **Sensors**: Simulated data for heart rate, oxygen level, temperature, and blood pressure is updated every second.
   - **Camera Feed**: Captures real-time video for visual situational awareness.
   - **Markers**: Randomly placed on the map with roles (fire, rescued individuals, firefighters) and interactive tooltips.

2. **Real-Time Interaction**:
   - **Interactive Map**:
     - Displays dynamic markers, each with a specific role and detailed information.
     - Selection of a marker highlights it and displays additional information in the side panel.
   - **Vital Signs Monitoring**:
     - Live graphs visualize trends for heart rate, oxygen, temperature, and blood pressure.
   - **Chat System**:
     - Enables bidirectional communication with a simulated chatbot.

3. **Visualization and Feedback**:
   - **Graphs**: Provide immediate insights into vital trends.
   - **Marker Details**: Clicking on a marker shows detailed information about the person or situation.
   - **Camera Feed**: Provides real-time video for enhanced context.

4. **Customization**:
   - The UI uses a custom palette for a professional look and feel.
   - Background gradients and animations add a polished aesthetic to the application.

---

#### **How to Run**
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd ElementEdge
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python app.py
   ```
4. Access the application at `http://127.0.0.1:8050` in your web browser.

---

#### **Future Improvements**
- Integration with real IoT sensors for live vital data.
- Adding predictive analytics using AI for early warnings.
- Expanding map functionalities with more granular geospatial data.
- Supporting AR-based visualization for enhanced situational awareness.

---
