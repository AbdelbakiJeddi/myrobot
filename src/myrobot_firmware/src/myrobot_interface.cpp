#include "myrobot_firmware/myrobot_interface.hpp"
#include <hardware_interface/types/hardware_interface_type_values.hpp>
#include <pluginlib/class_list_macros.hpp>
#include <hardware_interface/hardware_component_interface.hpp>
#include <algorithm>
#include <iomanip>

namespace myrobot_firmware
{
MyRobotInterface::MyRobotInterface()
{
}


MyRobotInterface::~MyRobotInterface()
{
  if (arduino_.IsOpen())
  {
    try
    {
      arduino_.Close();
    }
    catch (...)
    {
      RCLCPP_FATAL_STREAM(rclcpp::get_logger("MyRobotInterface"),
                          "Something went wrong while closing connection with port " << port_);
    }
  }
}


CallbackReturn MyRobotInterface::on_init(const hardware_interface::HardwareInfo & hardware_info)
{
  CallbackReturn result = hardware_interface::SystemInterface::on_init(hardware_info);
  if (result != CallbackReturn::SUCCESS)
  {
    return result;
  }

  // Validate joint count - this hardware interface supports at least 2 joints
  if (info_.joints.size() < 2)
  {
    RCLCPP_FATAL(rclcpp::get_logger("MyRobotInterface"),
                 "Expected at least 2 joints for diff_drive robot, got %zu", info_.joints.size());
    return CallbackReturn::FAILURE;
  }

  try
  {
    port_ = info_.hardware_parameters.at("port");
  }
  catch (const std::out_of_range &e)
  {
    RCLCPP_FATAL(rclcpp::get_logger("MyRobotInterface"), "No Serial Port provided! Aborting");
    return CallbackReturn::FAILURE;
  }

  velocity_commands_.resize(info_.joints.size(), 0.0);
  position_states_.resize(info_.joints.size(), 0.0);
  velocity_states_.resize(info_.joints.size(), 0.0);

  return CallbackReturn::SUCCESS;
}


std::vector<hardware_interface::StateInterface> MyRobotInterface::export_state_interfaces()
{
  std::vector<hardware_interface::StateInterface> state_interfaces;

  // Provide only a position Interface
  for (size_t i = 0; i < info_.joints.size(); i++)
  {
    state_interfaces.emplace_back(hardware_interface::StateInterface(
        info_.joints[i].name, hardware_interface::HW_IF_POSITION, &position_states_[i]));
    state_interfaces.emplace_back(hardware_interface::StateInterface(
        info_.joints[i].name, hardware_interface::HW_IF_VELOCITY, &velocity_states_[i]));
  }

  return state_interfaces;
}


std::vector<hardware_interface::CommandInterface> MyRobotInterface::export_command_interfaces()
{
  std::vector<hardware_interface::CommandInterface> command_interfaces;

  // Provide only a velocity Interface
  for (size_t i = 0; i < info_.joints.size(); i++)
  {
    command_interfaces.emplace_back(hardware_interface::CommandInterface(
        info_.joints[i].name, hardware_interface::HW_IF_VELOCITY, &velocity_commands_[i]));
  }

  return command_interfaces;
}


CallbackReturn MyRobotInterface::on_activate(const rclcpp_lifecycle::State &)
{
  RCLCPP_INFO(rclcpp::get_logger("MyRobotInterface"), "Starting robot hardware ...");

  // Reset commands and states
  std::fill(velocity_commands_.begin(), velocity_commands_.end(), 0.0);
  std::fill(position_states_.begin(), position_states_.end(), 0.0);
  std::fill(velocity_states_.begin(), velocity_states_.end(), 0.0);

  try
  {
    arduino_.Open(port_);
    arduino_.SetBaudRate(LibSerial::BaudRate::BAUD_115200);
  }
  catch (...)
  {
    RCLCPP_FATAL_STREAM(rclcpp::get_logger("MyRobotInterface"),
                        "Something went wrong while interacting with port " << port_);
    return CallbackReturn::FAILURE;
  }

  RCLCPP_INFO(rclcpp::get_logger("MyRobotInterface"),
              "Hardware started, ready to take commands");
  return CallbackReturn::SUCCESS;
}


CallbackReturn MyRobotInterface::on_deactivate(const rclcpp_lifecycle::State &)
{
  RCLCPP_INFO(rclcpp::get_logger("MyRobotInterface"), "Stopping robot hardware ...");

  if (arduino_.IsOpen())
  {
    try
    {
      arduino_.Close();
    }
    catch (...)
    {
      RCLCPP_FATAL_STREAM(rclcpp::get_logger("MyRobotInterface"),
                          "Something went wrong while closing connection with port " << port_);
    }
  }

  RCLCPP_INFO(rclcpp::get_logger("MyRobotInterface"), "Hardware stopped");
  return CallbackReturn::SUCCESS;
}


hardware_interface::return_type MyRobotInterface::read(const rclcpp::Time &, const rclcpp::Duration & period)
{
  auto dt = period.seconds();  // 0.01s

  // ✅ Always integrates every 10ms using last known velocity
  for (size_t i = 0; i < velocity_states_.size(); i++)
  {
    position_states_.at(i) += velocity_states_.at(i) * dt;
  }

  // ✅ Only updates velocity when Arduino sends new data (every 50ms)
  if (arduino_.IsDataAvailable())
  {
    std::string message;
    arduino_.ReadLine(message);
    std::stringstream ss(message);
    std::string res;

    while (std::getline(ss, res, ','))
    {
      if (res.length() < 3) continue;

      int multiplier = res.at(1) == 'p' ? 1 : -1;
      size_t joint_index = (res.at(0) == 'r') ? 0 : 1;

      if (joint_index >= info_.joints.size()) continue;

      try
      {
        double velocity = multiplier * std::stod(res.substr(2, res.size()));
        velocity_states_.at(joint_index) = velocity;  // update velocity only, position already integrated above
      }
      catch (const std::invalid_argument &e)
      {
        RCLCPP_WARN_STREAM(rclcpp::get_logger("MyRobotInterface"),
                           "Invalid data: " << res << " - skipping");
      }
    }
  }

  return hardware_interface::return_type::OK;
}


hardware_interface::return_type MyRobotInterface::write(const rclcpp::Time &,
                                                          const rclcpp::Duration &)
{
  // Implement communication protocol with the Arduino
  // Message format: "r<sign><velocity>,l<sign><velocity>" (e.g., "rp5.23,ln3.12")
  std::stringstream message_stream;

  message_stream << std::fixed << std::setprecision(2)
    << "r" << (velocity_commands_.at(0) >= 0 ? 'p' : 'n')
    << std::setw(5) << std::setfill('0') << std::abs(velocity_commands_.at(0))
    << ",l" << (velocity_commands_.at(1) >= 0 ? 'p' : 'n')
    << std::setw(5) << std::setfill('0') << std::abs(velocity_commands_.at(1))
    << ",";

  std::string message = message_stream.str();

  //RCLCPP_INFO_STREAM(rclcpp::get_logger("MyRobotInterface"), "TX: " << message);

  try
  {
    arduino_.Write(message);
  }
  catch (...)
  {
    RCLCPP_ERROR_STREAM(rclcpp::get_logger("MyRobotInterface"),
                        "Something went wrong while sending the message " << message << " to the port " << port_);
    return hardware_interface::return_type::ERROR;
  }

  return hardware_interface::return_type::OK;
}
}  // namespace myrobot_firmware

PLUGINLIB_EXPORT_CLASS(myrobot_firmware::MyRobotInterface, hardware_interface::SystemInterface)