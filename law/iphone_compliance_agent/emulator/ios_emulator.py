#!/usr/bin/env python3
"""
iPhone Emulator Integration Layer
Uses Appium to control iOS Simulator for app compliance testing
"""

import os
import time
import base64
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from appium import webdriver
from appium.options.ios import XCUITestOptions
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@dataclass
class AppSession:
    """Represents an active app testing session"""
    app_name: str
    bundle_id: str
    driver: webdriver.Remote
    start_time: float
    screenshots: List[str]
    interactions: List[Dict]


class iOSEmulator:
    """
    Manages iOS Simulator for app compliance testing

    Prerequisites:
    - Xcode installed (iOS Simulator)
    - Appium Server running (appium --allow-cors)
    - Python packages: appium-python-client, selenium
    """

    def __init__(self, device_name: str = "iPhone 15 Pro", platform_version: str = "17.0"):
        self.device_name = device_name
        self.platform_version = platform_version
        self.driver: Optional[webdriver.Remote] = None
        self.current_session: Optional[AppSession] = None
        self.screenshots_dir = "law/iphone_compliance_agent/reports/screenshots"
        os.makedirs(self.screenshots_dir, exist_ok=True)

    def connect(self, app_bundle_id: str, app_name: str) -> bool:
        """
        Connect to iOS Simulator and launch app

        Args:
            app_bundle_id: Bundle ID of the app (e.g., com.instagram.app)
            app_name: Human-readable app name

        Returns:
            True if connection successful
        """
        print(f"📱 Connecting to iOS Simulator...")
        print(f"   Device: {self.device_name} (iOS {self.platform_version})")
        print(f"   App: {app_name} ({app_bundle_id})")

        try:
            # Configure Appium options
            options = XCUITestOptions()
            options.platform_name = "iOS"
            options.platform_version = self.platform_version
            options.device_name = self.device_name
            options.bundle_id = app_bundle_id
            options.automation_name = "XCUITest"
            options.no_reset = False  # Fresh app state each time
            options.full_reset = False
            options.new_command_timeout = 300

            # Connect to Appium server (default: http://localhost:4723)
            self.driver = webdriver.Remote(
                command_executor="http://localhost:4723",
                options=options
            )

            # Wait for app to launch
            time.sleep(3)

            # Create session
            self.current_session = AppSession(
                app_name=app_name,
                bundle_id=app_bundle_id,
                driver=self.driver,
                start_time=time.time(),
                screenshots=[],
                interactions=[]
            )

            print(f"   ✅ Connected successfully")
            return True

        except Exception as e:
            print(f"   ❌ Connection failed: {e}")
            return False

    def take_screenshot(self, description: str = "") -> str:
        """
        Capture screenshot of current screen

        Args:
            description: Description of what's being captured

        Returns:
            Path to saved screenshot
        """
        if not self.driver:
            raise RuntimeError("Not connected to emulator")

        timestamp = int(time.time())
        filename = f"{self.current_session.app_name}_{timestamp}.png"
        filepath = os.path.join(self.screenshots_dir, filename)

        # Capture screenshot
        screenshot_b64 = self.driver.get_screenshot_as_base64()
        screenshot_bytes = base64.b64decode(screenshot_b64)

        # Save to file
        with open(filepath, "wb") as f:
            f.write(screenshot_bytes)

        # Record in session
        self.current_session.screenshots.append({
            "path": filepath,
            "description": description,
            "timestamp": timestamp
        })

        print(f"   📸 Screenshot saved: {filename}")
        if description:
            print(f"      Description: {description}")

        return filepath

    def get_screen_elements(self) -> List[Dict]:
        """
        Get all interactive elements on current screen

        Returns:
            List of element dictionaries with properties
        """
        if not self.driver:
            raise RuntimeError("Not connected to emulator")

        elements = []

        try:
            # Get all elements
            all_elements = self.driver.find_elements(AppiumBy.XPATH, "//*[@visible='true']")

            for elem in all_elements:
                try:
                    element_info = {
                        "type": elem.get_attribute("type"),
                        "name": elem.get_attribute("name"),
                        "label": elem.get_attribute("label"),
                        "value": elem.get_attribute("value"),
                        "enabled": elem.get_attribute("enabled"),
                        "visible": elem.get_attribute("visible"),
                        "rect": elem.rect,
                    }
                    elements.append(element_info)
                except:
                    continue

        except Exception as e:
            print(f"   ⚠️ Error getting elements: {e}")

        return elements

    def tap_element(self, element_name: str = None, x: int = None, y: int = None) -> bool:
        """
        Tap on element by name or coordinates

        Args:
            element_name: Accessibility ID or label of element
            x, y: Coordinates to tap (if element_name not provided)

        Returns:
            True if tap successful
        """
        if not self.driver:
            raise RuntimeError("Not connected to emulator")

        try:
            if element_name:
                # Find and tap element
                element = self.driver.find_element(AppiumBy.ACCESSIBILITY_ID, element_name)
                element.click()
                action = f"Tapped element: {element_name}"
            elif x and y:
                # Tap coordinates
                self.driver.tap([(x, y)])
                action = f"Tapped coordinates: ({x}, {y})"
            else:
                print("   ❌ Must provide element_name or coordinates")
                return False

            # Record interaction
            self.current_session.interactions.append({
                "action": action,
                "timestamp": time.time()
            })

            print(f"   👆 {action}")
            time.sleep(1)  # Wait for UI to respond
            return True

        except Exception as e:
            print(f"   ❌ Tap failed: {e}")
            return False

    def scroll_down(self, distance: int = 300) -> bool:
        """Scroll down on current screen"""
        if not self.driver:
            raise RuntimeError("Not connected to emulator")

        try:
            # Get screen dimensions
            size = self.driver.get_window_size()
            start_x = size['width'] // 2
            start_y = size['height'] * 0.8
            end_y = start_y - distance

            # Perform swipe (scroll)
            self.driver.swipe(start_x, start_y, start_x, end_y, duration=500)

            # Record interaction
            self.current_session.interactions.append({
                "action": f"Scrolled down {distance}px",
                "timestamp": time.time()
            })

            print(f"   ⬇️ Scrolled down")
            time.sleep(1)
            return True

        except Exception as e:
            print(f"   ❌ Scroll failed: {e}")
            return False

    def navigate_back(self) -> bool:
        """Navigate back (swipe from left edge or tap back button)"""
        if not self.driver:
            raise RuntimeError("Not connected to emulator")

        try:
            # Try to find back button first
            try:
                back_button = self.driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Back")
                back_button.click()
                print("   ⬅️ Tapped back button")
            except:
                # Swipe from left edge (iOS back gesture)
                size = self.driver.get_window_size()
                start_x = 10
                start_y = size['height'] // 2
                end_x = size['width'] // 2

                self.driver.swipe(start_x, start_y, end_x, start_y, duration=200)
                print("   ⬅️ Swiped back")

            # Record interaction
            self.current_session.interactions.append({
                "action": "Navigated back",
                "timestamp": time.time()
            })

            time.sleep(1)
            return True

        except Exception as e:
            print(f"   ❌ Navigate back failed: {e}")
            return False

    def get_page_source(self) -> str:
        """Get XML page source of current screen"""
        if not self.driver:
            raise RuntimeError("Not connected to emulator")

        return self.driver.page_source

    def execute_flow(self, flow_steps: List[Dict]) -> List[Dict]:
        """
        Execute a predefined navigation flow

        Args:
            flow_steps: List of step dictionaries with actions

        Returns:
            List of results for each step
        """
        if not self.driver:
            raise RuntimeError("Not connected to emulator")

        print(f"\n🔄 Executing flow with {len(flow_steps)} steps...")

        results = []
        for i, step in enumerate(flow_steps, 1):
            print(f"\n   Step {i}/{len(flow_steps)}: {step.get('description', 'No description')}")

            action = step.get("action")

            # Take screenshot before action
            screenshot = self.take_screenshot(f"Before: {step.get('description', '')}")

            # Execute action
            if action == "tap":
                success = self.tap_element(
                    element_name=step.get("element"),
                    x=step.get("x"),
                    y=step.get("y")
                )
            elif action == "scroll":
                success = self.scroll_down(step.get("distance", 300))
            elif action == "back":
                success = self.navigate_back()
            elif action == "wait":
                time.sleep(step.get("duration", 2))
                success = True
            else:
                print(f"   ⚠️ Unknown action: {action}")
                success = False

            # Take screenshot after action
            screenshot_after = self.take_screenshot(f"After: {step.get('description', '')}")

            # Get screen elements
            elements = self.get_screen_elements()

            results.append({
                "step": i,
                "description": step.get("description"),
                "action": action,
                "success": success,
                "screenshot_before": screenshot,
                "screenshot_after": screenshot_after,
                "elements_found": len(elements),
                "elements": elements[:10]  # Limit to first 10 for brevity
            })

        print(f"\n✅ Flow execution complete: {len(results)} steps")
        return results

    def get_session_summary(self) -> Dict:
        """Get summary of current testing session"""
        if not self.current_session:
            return {}

        duration = time.time() - self.current_session.start_time

        return {
            "app_name": self.current_session.app_name,
            "bundle_id": self.current_session.bundle_id,
            "duration_seconds": duration,
            "screenshots_captured": len(self.current_session.screenshots),
            "interactions_performed": len(self.current_session.interactions),
            "screenshots": self.current_session.screenshots,
            "interactions": self.current_session.interactions
        }

    def disconnect(self):
        """Close app and disconnect from emulator"""
        if self.driver:
            print(f"\n📱 Disconnecting from emulator...")

            # Get session summary before closing
            summary = self.get_session_summary()

            self.driver.quit()
            self.driver = None
            self.current_session = None

            print(f"   ✅ Disconnected")
            print(f"   📊 Session summary:")
            print(f"      Duration: {summary.get('duration_seconds', 0):.1f}s")
            print(f"      Screenshots: {summary.get('screenshots_captured', 0)}")
            print(f"      Interactions: {summary.get('interactions_performed', 0)}")

            return summary


def test_emulator():
    """Test emulator connection"""
    print("Testing iOS Emulator Integration\n")

    emulator = iOSEmulator()

    # Test connection (requires app to be installed in simulator)
    if emulator.connect("com.apple.mobilesafari", "Safari"):
        # Take initial screenshot
        emulator.take_screenshot("Home screen")

        # Get elements
        elements = emulator.get_screen_elements()
        print(f"\n   Found {len(elements)} elements on screen")

        # Disconnect
        emulator.disconnect()
    else:
        print("❌ Failed to connect to emulator")
        print("\nSetup instructions:")
        print("1. Install Xcode and iOS Simulator")
        print("2. Install Appium: npm install -g appium")
        print("3. Install XCUITest driver: appium driver install xcuitest")
        print("4. Start Appium server: appium --allow-cors")
        print("5. Ensure app is installed in simulator")


if __name__ == "__main__":
    test_emulator()
