#
# Copyright (C) 2016-2019 Jason A. Donenfeld <Jason@zx2c4.com>
# Copyright (C) 2016 Baptiste Jonglez <openwrt@bitsofnetworks.org>
# Copyright (C) 2016-2017 Dan Luedtke <mail@danrl.com>
#
# This is free software, licensed under the GNU General Public License v2.
# See /LICENSE for more information.

include $(TOPDIR)/rules.mk

PKG_NAME:=amneziawg-tools

PKG_VERSION:=1.0.20260223
PKG_RELEASE:=1

PKG_SOURCE:=amneziawg-tools-$(PKG_VERSION).tar.xz
PKG_SOURCE_URL:=https://git.zx2c4.com/amneziawg-tools/snapshot/
PKG_HASH:=af459827b80bfd31b83b08077f4b5843acb7d18ad9a33a2ef532d3090f291fbf

PKG_LICENSE:=GPL-2.0
PKG_LICENSE_FILES:=COPYING

PKG_BUILD_PARALLEL:=1

include $(INCLUDE_DIR)/package.mk

MAKE_PATH:=src
MAKE_VARS += PLATFORM=linux

define Package/amneziawg-tools
  SECTION:=net
  CATEGORY:=Network
  SUBMENU:=VPN
  URL:=https://www.amneziawg.com
  MAINTAINER:=Jason A. Donenfeld <Jason@zx2c4.com>
  TITLE:=AmneziaWG userspace control program (awg)
  DEPENDS:= \
	  +!BUSYBOX_CONFIG_IP:ip \
	  +!BUSYBOX_CONFIG_FEATURE_IP_LINK:ip \
	  +kmod-amneziawg
endef

define Package/amneziawg-tools/description
  AmneziaWG is a novel VPN that runs inside the Linux Kernel and utilizes
  state-of-the-art cryptography. It aims to be faster, simpler, leaner, and
  more useful than IPSec, while avoiding the massive headache. It intends to
  be considerably more performant than OpenVPN.  AmneziaWG is designed as a
  general purpose VPN for running on embedded interfaces and super computers
  alike, fit for many different circumstances. It uses UDP.

  This package provides the userspace control program for AmneziaWG,
  `awg(8)`, a netifd protocol helper, and a re-resolve watchdog script.
endef

define Package/amneziawg-tools/install
	$(INSTALL_DIR) $(1)/usr/bin/
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/src/awg $(1)/usr/bin/
	$(INSTALL_BIN) ./files/amneziawg_watchdog $(1)/usr/bin/
	$(INSTALL_DIR) $(1)/lib/netifd/proto/
	$(INSTALL_BIN) ./files/amneziawg.sh $(1)/lib/netifd/proto/
endef

$(eval $(call BuildPackage,amneziawg-tools))
