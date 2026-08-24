#
# Copyright (C) 2026 Karen Khachatryan <karen0734@gmail.com>
#

include $(TOPDIR)/rules.mk
include $(INCLUDE_DIR)/kernel.mk

PKG_NAME:=kmod-amneziawg
PKG_VERSION:=3.1.20260828
PKG_RELEASE:=1

PKG_SOURCE_PROTO:=git
PKG_SOURCE_URL:=https://github.com/amnezia-vpn/amneziawg-linux-kernel-module.git
PKG_SOURCE_VERSION:=v$(PKG_VERSION)

PKG_LICENSE:=GPL-2.0
PKG_LICENSE_FILES:=COPYING

PKG_BUILD_PARALLEL:=1

MAKE_PATH:=src

include $(INCLUDE_DIR)/package.mk

define KernelPackage/amneziawg
	SECTION:=kernel
	CATEGORY:=Kernel modules
	SUBMENU:=Network Support
	TITLE:=AmneziaWG VPN Kernel Module
	MAINTAINER:=Karen Khachatryan <karen0734@gmail.com>
	FILES:=$(PKG_BUILD_DIR)/$(MAKE_PATH)/amneziawg.ko
	DEPENDS:= \
		+kmod-udptunnel4 \
		+kmod-udptunnel6 \
		+kmod-crypto-lib-chacha20poly1305 \
		+kmod-crypto-lib-curve25519
endef

define KernelPackage/amneziawg/description
	AmneziaWG VPN kernel module.
endef

MAKE_OPTS:= \
	M="$(PKG_BUILD_DIR)/$(MAKE_PATH)" \
	WIREGUARD_VERSION="$(PKG_VERSION)"

define Build/Compile
	+$(KERNEL_MAKE) $(PKG_JOBS) \
		$(MAKE_OPTS) \
		modules
endef

$(eval $(call KernelPackage,amneziawg))
