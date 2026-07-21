#include "myrobot_hardware/myrobot_hardware_interface.hpp"
#include <hardware_interface/types/hardware_interface_type_values.hpp>
#include <pluginlib/class_list_macros.hpp>
#include <hardware_interface/hardware_component_interface.hpp>
#include <algorithm>
#include <iomanip>

namespace myrobot_hardware
{

MyRobotHardwareInterface::MyRobotHardwareInterface()
{
}

MyRobotHardwareInterface::~MyRobotHardwareInterface()
{
  if (arduino_.IsOpen())
  {
    try
    {
      arduino_.Close();
    }
    catch (...)
    {
      RCLCPP_FATAL_STREAM(rclcpp::get_logger("MyRobotHardwareInterface"),
                          "Something went wrong while closing connection with port " << port_);
    }
  }
}

CallbackReturn MyRobotHardwareInterface::on_init(const hardware_interface::HardwareInfo & hardware_info)
{
  CallbackReturn result = hardware_interface::SystemInterface::on_init(hardware_info);
  if (result != CallbackReturn::SUCCESS)
  {
    return result;
  }

  if (info_.joints.size() < 2)
  {
    RCLCPP_FATAL(rclcpp::get_logger("MyRobotHardwareInterface"),
                 "Expected at least 2 joints for diff_drive robot, got %zu", info_.joints.size());
    return CallbackReturn::FAILURE;
  }

  try
  {
    port_ = info_.hardware_parameters.at("port");
  }
  catch (const std::out_of_range &e)
  {
    RCLCPP_FATAL(rclcpp::get_logger("MyRobotHardwareInterface"), "No Serial Port provided! Aborting");
    return CallbackReturn::FAILURE;
  }

  velocity_commands_.resize(info_.joints.size(), 0.0);
  position_states_.resize(info_.joints.size(), 0.0);
  velocity_states_.resize(info_.joints.size(), 0.0);

  return CallbackReturn::SUCCESS;
}

std::vector<hardware_interface::StateInterface> MyRobotHardwareInterface::export_state_interfaces()
{
  std::vector<hardware_interface::StateInterface> state_interfaces;

  for (size_t i = 0; i < info_.joints.size(); i++)
  {
    state_interfaces.emplace_back(hardware_interface::StateInterface(
        info_.joints[i].name, hardware_interface::HW_IF_POSITION, &position_states_[i]));
    state_interfaces.emplace_back(hardware_interface::StateInterface(
        info_.joints[i].name, hardware_interface::HW_IF_VELOCITY, &velocity_states_[i]));
  }

  return state_interfaces;
}

std::vector<hardware_interface::CommandInterface> MyRobotHardwareInterface::export_command_interfaces()
{
  std::vector<hardware_interface::CommandInterface> command_interfaces;

  for (size_t i = 0; i < info_.joints.size(); i++)
  {
    command_interfaces.emplace_back(hardware_interface::CommandInterface(
        info_.joints[i].name, hardware_interface::HW_IF_VELOCITY, &velocity_commands_[i]));
  }

  return command_interfaces;
}

CallbackReturn MyRobotHardwareInterface::on_activate(const rclcpp_lifecycle::State &)
{
  RCLCPP_INFO(rclcpp::get_logger("MyRobotHardwareInterface"), "Starting robot hardware ...");

  std::fill(velocity_commands_.begin(), velocity_commands_.end(), 0.0);
  std::fill(position_states_.begin(), position_states_.end(), 0.0);
  std::fill(velocity_states_.begin(), velocity_states_.end(), 0.0);

  try
  {
    arduino_.Open(port_);
    arduino_.SetBaudRate(LibSerial::BaudRate::BAUD_115200);
    std::this_thread::sleep_for(std::chrono::seconds(2));
  }
  catch (...)
  {
    RCLCPP_FATAL_STREAM(rclcpp::get_logger("MyRobotHardwareInterface"),
                        "Something went wrong while interacting with port " << port_);
    return CallbackReturn::FAILURE;
  }

  RCLCPP_INFO(rclcpp::get_logger("MyRobotHardwareInterface"),
              "Hardware started, ready to take commands");
  return CallbackReturn::SUCCESS;
}

CallbackReturn MyRobotHardwareInterface::on_deactivate(const rclcpp_lifecycle::State &)
{
  RCLCPP_INFO(rclcpp::get_logger("MyRobotHardwareInterface"), "Stopping robot hardware ...");

  if (arduino_.IsOpen())
  {
    try
    {
      arduino_.Close();
    }
    catch (...)
    {
      RCLCPP_FATAL_STREAM(rclcpp::get_logger("MyRobotHardwareInterface"),
                          "Something went wrong while closing connection with port " << port_);
    }
  }

  RCLCPP_INFO(rclcpp::get_logger("MyRobotHardwareInterface"), "Hardware stopped");
  return CallbackReturn::SUCCESS;
}

hardware_interface::return_type MyRobotHardwareInterface::read(const rclcpp::Time &, const rclcpp::Duration & period)
{
  auto dt = period.seconds();

  for (size_t i = 0; i < velocity_states_.size(); i++)
  {
    position_states_.at(i) += velocity_states_.at(i) * dt;
  }

  if (arduino_.IsDataAvailable())
  {
    std::string message;
    try {
      arduino_.ReadLine(message, '\n', 2);
    }
    catch (const LibSerial::ReadTimeout &)
    {
      return hardware_interface::return_type::OK;
    }

    if (message.empty()) {
      return hardware_interface::return_type::OK;
    }

    std::stringstream ss(message);
    std::string res;

    while (std::getline(ss, res, ','))
    {
      if (res.length() < 3) continue;

      char side = res.at(0);
      char sign = res.at(1);
      int multiplier = (sign == 'p') ? 1 : -1;

      try
      {
        double val = std::stod(res.substr(2));

        if (side == 'r') {
          velocity_states_.at(0) = val * multiplier;
        } else if (side == 'l') {
          velocity_states_.at(1) = val * multiplier;
        }
      }
      catch (const std::invalid_argument &e)
      {
        RCLCPP_WARN_THROTTLE(rclcpp::get_logger("MyRobotHardwareInterface"),
                               *get_clock(), 1000,
                               "Data conversion failed for '%s': %s", res.c_str(), e.what());
        continue;
      }
    }
  }

  return hardware_interface::return_type::OK;
}

hardware_interface::return_type MyRobotHardwareInterface::write(const rclcpp::Time &,
                                                                const rclcpp::Duration &)
{
  std::stringstream message_stream;

  message_stream << std::fixed << std::setprecision(2)
    << "r" << (velocity_commands_.at(0) >= 0 ? 'p' : 'n')
    << std::setw(5) << std::setfill('0') << std::abs(velocity_commands_.at(0))
    << ",l" << (velocity_commands_.at(1) >= 0 ? 'p' : 'n')
    << std::setw(5) << std::setfill('0') << std::abs(velocity_commands_.at(1))
    << ",";

  std::string message = message_stream.str();

  try
  {
    arduino_.Write(message);
  }
  catch (...)
  {
    RCLCPP_ERROR_STREAM(rclcpp::get_logger("MyRobotHardwareInterface"),
                        "Something went wrong while sending the message " << message << " to the port " << port_);
    return hardware_interface::return_type::ERROR;
  }

  return hardware_interface::return_type::OK;
}

}  // namespace myrobot_hardware

PLUGINLIB_EXPORT_CLASS(myrobot_hardware::MyRobotHardwareInterface, hardware_interface::SystemInterface)
