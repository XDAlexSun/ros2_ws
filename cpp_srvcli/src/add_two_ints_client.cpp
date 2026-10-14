// #include <chrono>
// #include <cinttypes>
// #include <memory>

// #include "example_interfaces/srv/add_two_ints.hpp"
// #include "rclcpp/rclcpp.hpp"

// using AddTwoInts = example_interfaces::srv::AddTwoInts;

// int main(int argc, char * argv[])
// {
//   rclcpp::init(argc, argv);
//   auto node = rclcpp::Node::make_shared("minimal_client");
//   auto client = node->create_client<AddTwoInts>("add_two_ints");
//   while (!client->wait_for_service(std::chrono::seconds(1))) {
//     if (!rclcpp::ok()) {
//       RCLCPP_ERROR(node->get_logger(), "client interrupted while waiting for service to appear.");
//       return 1;
//     }
//     RCLCPP_INFO(node->get_logger(), "waiting for service to appear...");
//   }
//   auto request = std::make_shared<AddTwoInts::Request>();
//   request->a = 41;
//   request->b = 1;
//   auto result_future = client->async_send_request(request);
//   if (rclcpp::spin_until_future_complete(node, result_future) !=
//     rclcpp::FutureReturnCode::SUCCESS)
//   {
//     RCLCPP_ERROR(node->get_logger(), "service call failed :(");
//     client->remove_pending_request(result_future);
//     return 1;
//   }
//   auto result = result_future.get();
//   RCLCPP_INFO(
//     node->get_logger(), "result of %" PRId64 " + %" PRId64 " = %" PRId64,
//     request->a, request->b, result->sum);
//   rclcpp::shutdown();
//   return 0;
// }

#include "rclcpp/rclcpp.hpp"
#include "tutorial_interfaces/srv/add_three_ints.hpp"                                       // CHANGE

#include <chrono>
#include <cstdlib>
#include <memory>

using namespace std::chrono_literals;

int main(int argc, char **argv)
{
  rclcpp::init(argc, argv);

  std::shared_ptr<rclcpp::Node> node = rclcpp::Node::make_shared("add_three_ints_client");  // CHANGE
  rclcpp::Client<tutorial_interfaces::srv::AddThreeInts>::SharedPtr client =                // CHANGE
    node->create_client<tutorial_interfaces::srv::AddThreeInts>("add_three_ints");          // CHANGE

  auto request = std::make_shared<tutorial_interfaces::srv::AddThreeInts::Request>();       // CHANGE
  request->a = 41;
  request->b = 1;
  request->c = 1;                                                                           // CHANGE

  while (!client->wait_for_service(1s)) {
    if (!rclcpp::ok()) {
      RCLCPP_ERROR(rclcpp::get_logger("rclcpp"), "Interrupted while waiting for the service. Exiting.");
      return 0;
    }
    RCLCPP_INFO(rclcpp::get_logger("rclcpp"), "service not available, waiting again...");
  }

  auto result = client->async_send_request(request);
  // Wait for the result.
  if (rclcpp::spin_until_future_complete(node, result) ==
    rclcpp::FutureReturnCode::SUCCESS)
  {
    RCLCPP_INFO(rclcpp::get_logger("rclcpp"), "Sum: %ld", result.get()->sum);
  } else {
    RCLCPP_ERROR(rclcpp::get_logger("rclcpp"), "Failed to call service add_three_ints");    // CHANGE
  }

  rclcpp::shutdown();
  return 0;
}