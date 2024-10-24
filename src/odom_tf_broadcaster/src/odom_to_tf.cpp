#include <rclcpp/rclcpp.hpp>
#include <nav_msgs/msg/odometry.hpp>
#include <tf2_ros/transform_broadcaster.h>
#include <geometry_msgs/msg/transform_stamped.hpp>

class OdomToTF : public rclcpp::Node
{
public:
    OdomToTF() : Node("odom_to_tf")
    {
        // サブスクライバの設定
        odom_subscription_ = this->create_subscription<nav_msgs::msg::Odometry>(
            "/whill/odom", 10,
            [this](const nav_msgs::msg::Odometry::SharedPtr msg) { this->odom_callback(msg); });

        // TransformBroadcasterの初期化
        tf_broadcaster_ = std::make_shared<tf2_ros::TransformBroadcaster>(this);
    }

private:
    void odom_callback(const nav_msgs::msg::Odometry::SharedPtr msg)
    {
        auto t = geometry_msgs::msg::TransformStamped();

        // タイムスタンプとフレームIDの設定
        t.header.stamp = this->get_clock()->now();
        t.header.frame_id = "odom";  // 親フレーム
        t.child_frame_id = "base_link";  // 子フレーム

        // 位置の設定
        t.transform.translation.x = msg->pose.pose.position.x;
        t.transform.translation.y = msg->pose.pose.position.y;
        t.transform.translation.z = msg->pose.pose.position.z;

        // オリエンテーションの設定
        t.transform.rotation = msg->pose.pose.orientation;

        // TFのパブリッシュ
        tf_broadcaster_->sendTransform(t);
    }

    rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr odom_subscription_;
    std::shared_ptr<tf2_ros::TransformBroadcaster> tf_broadcaster_;
};

int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<OdomToTF>());
    rclcpp::shutdown();
    return 0;
}
