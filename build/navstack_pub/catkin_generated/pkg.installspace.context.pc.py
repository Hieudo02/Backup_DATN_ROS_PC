# generated from catkin/cmake/template/pkg.context.pc.in
CATKIN_PACKAGE_PREFIX = ""
PROJECT_PKG_CONFIG_INCLUDE_DIRS = "${prefix}/include".split(';') if "${prefix}/include" != "" else []
PROJECT_CATKIN_DEPENDS = "geometry_msgs;move_base;nav_msgs;roscpp;rospy;sensor_msgs;std_msgs;tf;tf2_ros".replace(';', ' ')
PKG_CONFIG_LIBRARIES_WITH_PREFIX = "-lnavstack_pub".split(';') if "-lnavstack_pub" != "" else []
PROJECT_NAME = "navstack_pub"
PROJECT_SPACE_DIR = "/home/hieudo/datn_navbot/install"
PROJECT_VERSION = "0.0.0"