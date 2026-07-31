#include "myrobot_hardware/myrobot_hardware_interface.hpp"
#include <hardware_interface/types/hardware_interface_type_values.hpp>
#include <pluginlib/class_list_macros.hpp>
#include <hardware_interface/hardware_component_interface.hpp>
#include <algorithm>
#include <iomanip>

namespace myrobot_hardware
{
  constexpr int LEFT_WHEEL = 0;
  constexpr int RIGHT_WHEEL = 1;

  constexpr double ENCODER_TICKS_PER_REV = 4096.0;
  constexpr double TWO_PI = 6.28318530718;

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

  CallbackReturn MyRobotHardwareInterface::on_init(const hardware_interface::HardwareInfo &hardware_info)
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
      std::this_thread::sleep_for(std::chrono::seconds(1));
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

  hardware_interface::return_type MyRobotHardwareInterface::read(const rclcpp::Time &, const rclcpp::Duration &)
  {
    if (!arduino_.IsDataAvailable())
    {
      return hardware_interface::return_type::OK;
    }

    std::string message;

    try
    {
      arduino_.ReadLine(message, '\n', 5);
    }
    catch (const LibSerial::ReadTimeout &)
    {
      return hardware_interface::return_type::OK;
    }

    long left_ticks;
    long right_ticks;

    double left_vel;
    double right_vel;

    /*
      Expected ESP32 message:

      L:12345,4.2,R:12400,4.3

    */

    int result = sscanf(message.c_str(), "L:%ld,%lf,R:%ld,%lf", &left_ticks, &left_vel, &right_ticks, &right_vel);

    if (result == 4)
    {
      position_states_[LEFT_WHEEL] = (left_ticks / ENCODER_TICKS_PER_REV) * TWO_PI;

      position_states_[RIGHT_WHEEL] = (right_ticks / ENCODER_TICKS_PER_REV) * TWO_PI;

      velocity_states_[LEFT_WHEEL] = left_vel;

      velocity_states_[RIGHT_WHEEL] = right_vel;
    }

    return hardware_interface::return_type::OK;
  }

  hardware_interface::return_type MyRobotHardwareInterface::write(const rclcpp::Time &, const rclcpp::Duration &)
  {
    std::stringstream message;

    message << "L:" << std::fixed << std::setprecision(3) << velocity_commands_[LEFT_WHEEL]
            << ",R:" << velocity_commands_[RIGHT_WHEEL] << "\n";

    try
    {
      arduino_.Write(message.str());
    }
    catch (...)
    {
      RCLCPP_ERROR(
          rclcpp::get_logger("MyRobotHardwareInterface"),
          "Failed sending velocity command");

      return hardware_interface::return_type::ERROR;
    }

    return hardware_interface::return_type::OK;
  }
}
PLUGINLIB_EXPORT_CLASS(myrobot_hardware::MyRobotHardwareInterface, hardware_interface::SystemInterface)
