# Copyright 2023 nacky823
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from launch import LaunchDescription
from launch.actions import OpaqueFunction
from launch_ros.actions import SetParameter
from launch_ros.actions import ComposableNodeContainer
from launch_ros.descriptions import ComposableNode


def launch_setup(context, *args, **kwargs):
    set_use_sim_time = SetParameter(name="use_sim_time", value=True)
    return [set_use_sim_time]

def generate_launch_description():
    launch_setup_func = OpaqueFunction(function=launch_setup)

    ns = "pointcloud_preprocessor"
    pkg = "pointcloud_preprocessor"

    crop_box_component = ComposableNode(
        package = pkg,
        plugin = "pointcloud_preprocessor::CropBoxFilterComponent",
        name = "crop_box_filter",
        remappings = [
            ("input", "velodyne_points"),
            # ("input", "ray/pointcloud2")
            ("output", "filtered_points/crop_box"),
        ],
        parameters = [
            {
                "input_frame": "velodyne",
                "output_frame": "velodyne",
                "min_x": -200.0,
                "max_x": 200.0,
                "min_y": -50.0,
                "max_y": 50.0,
                "min_z": -5.0,
                "max_z": 5.0,
                "negative": False,
            }
        ],
    )

    voxel_grid_component = ComposableNode(
        package = pkg,
        plugin = "pointcloud_preprocessor::VoxelGridDownsampleFilterComponent",
        name = "voxel_grid_filter",
        remappings = [
            ("input", "filtered_points/crop_box"),
            ("output", "filtered_points/voxel_grid"),
        ],
        parameters = [
            {
                "input_frame": "velodyne",
                "output_frame": "velodyne",
                "voxel_size_x": 0.3,
                "voxel_size_y": 0.3,
                "voxel_size_z": 0.3,
            }
        ],
    )

    random_downsample_component = ComposableNode(
        package = pkg,
        plugin = "pointcloud_preprocessor::RandomDownsampleFilterComponent",
        name = "random_downsample_filter",
        remappings = [
            ("input", "filtered_points/voxel_grid"),
            ("output", "filtered_points/random_downsample"),
        ],
        parameters = [
            {
                "input_frame": "velodyne",
                "output_frame": "velodyne",
                "sample_num": 3000,
            }
        ],
    )

    container = ComposableNodeContainer(
        name = "pointcloud_preprocessor_container",
        namespace = ns,
        package = "rclcpp_components",
        executable = "component_container",
        composable_node_descriptions = [
            crop_box_component,
            voxel_grid_component,
            random_downsample_component,
        ],
        output = "screen",
    )

    ld = LaunchDescription()

    ld.add_action(launch_setup_func)
    ld.add_action(container)

    return ld