#
# Copyright (C) 2016 Dan Luedtke <mail@danrl.com>
# Copyright (C) 2026 Karen Khachatryan <karen0734@gmail.com>
#
# This is free software, licensed under the Apache License, Version 2.0 .
#

include $(TOPDIR)/rules.mk

PKG_VERSION:=3.1.0

LUCI_NAME:=luci-proto-amneziawg

LUCI_TITLE:=Support for AmneziaWG VPN
LUCI_DEPENDS:=+amneziawg-tools +ucode +luci-lib-uqr +resolveip
LUCI_PKGARCH:=all

PKG_LICENSE:=Apache-2.0
PKG_MAINTAINER:=Karen Khachatryan <karen0734@gmail.com>

include $(TOPDIR)/feeds/luci/luci.mk

# call BuildPackage - OpenWrt buildroot signature
