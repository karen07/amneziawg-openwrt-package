# AmneziaWG OpenWrt

OpenWrt package definitions and build automation for AmneziaWG, including the kernel
module, userspace tools, and LuCI protocol support. The repository also provides automated
builds for supported OpenWrt targets.

Определения пакетов и автоматизация сборки AmneziaWG для OpenWrt: модуль ядра,
пользовательские утилиты и поддержка протокола в LuCI. Репозиторий также содержит
автоматическую сборку пакетов для поддерживаемых платформ OpenWrt.

## Описание

Вместо поддержки крупного ручного форка пакетов WireGuard для OpenWrt проект заново генерирует пакеты AmneziaWG из чистых исходников WireGuard для OpenWrt и LuCI. `generate.py` последовательно применяет к этой базе переименования и изменения, необходимые AmneziaWG.

Общая логика сборки через OpenWrt SDK и генерации матрицы CI вынесена в [openwrt-package-ci](https://github.com/karen07/openwrt-package-ci). В этом репозитории остаются исходники пакетов, `generate.py` и параметры конкретной сборки в `openwrt-build.env`.

[![Build OpenWrt AmneziaWG packages](https://github.com/karen07/amneziawg-openwrt-package/actions/workflows/openwrt-build.yml/badge.svg)](https://github.com/karen07/amneziawg-openwrt-package/actions/workflows/openwrt-build.yml)

## Содержание

- [Навигация](#%D0%BD%D0%B0%D0%B2%D0%B8%D0%B3%D0%B0%D1%86%D0%B8%D1%8F)
- [Разработка и проверка изменений](#%D1%80%D0%B0%D0%B7%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D0%BA%D0%B0-%D0%B8-%D0%BF%D1%80%D0%BE%D0%B2%D0%B5%D1%80%D0%BA%D0%B0-%D0%B8%D0%B7%D0%BC%D0%B5%D0%BD%D0%B5%D0%BD%D0%B8%D0%B9)
- [Сборка и установка](#%D1%81%D0%B1%D0%BE%D1%80%D0%BA%D0%B0-%D0%B8-%D1%83%D1%81%D1%82%D0%B0%D0%BD%D0%BE%D0%B2%D0%BA%D0%B0)
  - [Установка на роутер](#%D1%83%D1%81%D1%82%D0%B0%D0%BD%D0%BE%D0%B2%D0%BA%D0%B0-%D0%BD%D0%B0-%D1%80%D0%BE%D1%83%D1%82%D0%B5%D1%80)
  - [Сборка для роутера без установки](#%D1%81%D0%B1%D0%BE%D1%80%D0%BA%D0%B0-%D0%B4%D0%BB%D1%8F-%D1%80%D0%BE%D1%83%D1%82%D0%B5%D1%80%D0%B0-%D0%B1%D0%B5%D0%B7-%D1%83%D1%81%D1%82%D0%B0%D0%BD%D0%BE%D0%B2%D0%BA%D0%B8)
  - [Сборка с явными target/subtarget/pkgarch](#%D1%81%D0%B1%D0%BE%D1%80%D0%BA%D0%B0-%D1%81-%D1%8F%D0%B2%D0%BD%D1%8B%D0%BC%D0%B8-targetsubtargetpkgarch)
  - [Матрица GitHub Actions](#%D0%BC%D0%B0%D1%82%D1%80%D0%B8%D1%86%D0%B0-github-actions)
  - [Процесс GitHub Actions](#%D0%BF%D1%80%D0%BE%D1%86%D0%B5%D1%81%D1%81-github-actions)
  - [Артефакты релиза](#%D0%B0%D1%80%D1%82%D0%B5%D1%84%D0%B0%D0%BA%D1%82%D1%8B-%D1%80%D0%B5%D0%BB%D0%B8%D0%B7%D0%B0)
  - [Генерация из upstream-пакетов WireGuard](#%D0%B3%D0%B5%D0%BD%D0%B5%D1%80%D0%B0%D1%86%D0%B8%D1%8F-%D0%B8%D0%B7-upstream-%D0%BF%D0%B0%D0%BA%D0%B5%D1%82%D0%BE%D0%B2-wireguard)
  - [Установка готовых `.apk`](#%D1%83%D1%81%D1%82%D0%B0%D0%BD%D0%BE%D0%B2%D0%BA%D0%B0-%D0%B3%D0%BE%D1%82%D0%BE%D0%B2%D1%8B%D1%85-apk)
- [Что входит в проект](#%D1%87%D1%82%D0%BE-%D0%B2%D1%85%D0%BE%D0%B4%D0%B8%D1%82-%D0%B2-%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82)
- [Чем этот проект отличается](#%D1%87%D0%B5%D0%BC-%D1%8D%D1%82%D0%BE%D1%82-%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82-%D0%BE%D1%82%D0%BB%D0%B8%D1%87%D0%B0%D0%B5%D1%82%D1%81%D1%8F)
  - [1. Автопатч исходного WireGuard](#1-%D0%B0%D0%B2%D1%82%D0%BE%D0%BF%D0%B0%D1%82%D1%87-%D0%B8%D1%81%D1%85%D0%BE%D0%B4%D0%BD%D0%BE%D0%B3%D0%BE-wireguard)
  - [2. Отдельный пакет модуля ядра OpenWrt](#2-%D0%BE%D1%82%D0%B4%D0%B5%D0%BB%D1%8C%D0%BD%D1%8B%D0%B9-%D0%BF%D0%B0%D0%BA%D0%B5%D1%82-%D0%BC%D0%BE%D0%B4%D1%83%D0%BB%D1%8F-%D1%8F%D0%B4%D1%80%D0%B0-openwrt)
  - [3. Нормальная цепочка зависимостей пакетов](#3-%D0%BD%D0%BE%D1%80%D0%BC%D0%B0%D0%BB%D1%8C%D0%BD%D0%B0%D1%8F-%D1%86%D0%B5%D0%BF%D0%BE%D1%87%D0%BA%D0%B0-%D0%B7%D0%B0%D0%B2%D0%B8%D1%81%D0%B8%D0%BC%D0%BE%D1%81%D1%82%D0%B5%D0%B9-%D0%BF%D0%B0%D0%BA%D0%B5%D1%82%D0%BE%D0%B2)
  - [4. Поддержка готовых сборок и локальной разработки](#4-%D0%BF%D0%BE%D0%B4%D0%B4%D0%B5%D1%80%D0%B6%D0%BA%D0%B0-%D0%B3%D0%BE%D1%82%D0%BE%D0%B2%D1%8B%D1%85-%D1%81%D0%B1%D0%BE%D1%80%D0%BE%D0%BA-%D0%B8-%D0%BB%D0%BE%D0%BA%D0%B0%D0%BB%D1%8C%D0%BD%D0%BE%D0%B9-%D1%80%D0%B0%D0%B7%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D0%BA%D0%B8)
  - [5. Сборки OpenWrt 25.12+ на основе APK](#5-%D1%81%D0%B1%D0%BE%D1%80%D0%BA%D0%B8-openwrt-2512-%D0%BD%D0%B0-%D0%BE%D1%81%D0%BD%D0%BE%D0%B2%D0%B5-apk)
- [Что добавляется поверх WireGuard](#%D1%87%D1%82%D0%BE-%D0%B4%D0%BE%D0%B1%D0%B0%D0%B2%D0%BB%D1%8F%D0%B5%D1%82%D1%81%D1%8F-%D0%BF%D0%BE%D0%B2%D0%B5%D1%80%D1%85-wireguard)
- [Для кого этот проект](#%D0%B4%D0%BB%D1%8F-%D0%BA%D0%BE%D0%B3%D0%BE-%D1%8D%D1%82%D0%BE%D1%82-%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82)
- [Не цели проекта](#%D0%BD%D0%B5-%D1%86%D0%B5%D0%BB%D0%B8-%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0)
- [Краткая памятка](#%D0%BA%D1%80%D0%B0%D1%82%D0%BA%D0%B0%D1%8F-%D0%BF%D0%B0%D0%BC%D1%8F%D1%82%D0%BA%D0%B0)
- [Лицензия](#%D0%BB%D0%B8%D1%86%D0%B5%D0%BD%D0%B7%D0%B8%D1%8F)

## Навигация

Для установки пакета на роутер см. раздел
[Сборка и установка](#%D1%81%D0%B1%D0%BE%D1%80%D0%BA%D0%B0-%D0%B8-%D1%83%D1%81%D1%82%D0%B0%D0%BD%D0%BE%D0%B2%D0%BA%D0%B0).
Если нужно собирать или публиковать пакеты для нескольких целей,
смотрите [Матрица GitHub Actions](#%D0%BC%D0%B0%D1%82%D1%80%D0%B8%D1%86%D0%B0-github-actions) и
[Артефакты релиза](#%D0%B0%D1%80%D1%82%D0%B5%D1%84%D0%B0%D0%BA%D1%82%D1%8B-%D1%80%D0%B5%D0%BB%D0%B8%D0%B7%D0%B0).
Раздел [Чем этот проект отличается](#%D1%87%D0%B5%D0%BC-%D1%8D%D1%82%D0%BE%D1%82-%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82-%D0%BE%D1%82%D0%BB%D0%B8%D1%87%D0%B0%D0%B5%D1%82%D1%81%D1%8F)
объясняет отличия от обычных пакетов WireGuard.

## Разработка и проверка изменений

**Опорные символы для изменения поведения:**

1. `generate.py:AwgOpt` и `generate.py:run` - модель опций и стадии генерации пакетов; перед
   правкой файла пакета проверяйте, не перезаписывается ли он генератором.
1. `proto_amneziawg_setup`, `proto_amneziawg_teardown` - жизненный цикл сетевого протокола в
   `amneziawg-tools/files/amneziawg.sh`; изменение опций затрагивает также UCI и LuCI.

**Основные точки изменения:**

- `generate.py` - генерация/обновление определений пакетов из upstream;
- `amneziawg/Makefile` - параметры kernel module;
- `amneziawg-tools/Makefile` - userspace-утилиты;
- `luci-proto-amneziawg/Makefile` - компонент LuCI;
- `luci-proto-amneziawg/root/usr/share/luci/menu.d/luci-proto-amneziawg.json` -
  маршрут страницы состояния и зависимость от разрешения LuCI ACL;
- `luci-proto-amneziawg/root/usr/share/rpcd/acl.d/luci-amneziawg.json` -
  разрешения для чтения статуса и вызовов генерации ключей через ubus;
- `amneziawg-tools/files/amneziawg.sh` - интеграция протокола с OpenWrt;
- `openwrt-build.env` - параметры CI;
- `.github/workflows/openwrt-build.yml` - автоматическая сборка.

**Восстановление этапов генерации:** `rebuild-commits.sh` последовательно вызывает
`generate.py` для стадий `vanilla`, `files`, `text` и `full`, делая отдельный
Git-коммит после каждой стадии. Скрипт меняет рабочее дерево и историю коммитов;
для обычной правки пакета он не нужен. Перед его использованием проверяйте
состояние Git и ожидаемый результат генерации.

**Граница UI и прав:** запись нового действия в LuCI требует проверить не только
страницу, но и `menu.d` и `rpcd/acl.d`. В ACL чтение `getAwgInstances`
отличается от разрешённых операций генерации ключей
`generateKeyPair`, `getPublicAndPrivateKeyFromPrivate` и `generatePsk`.
Изменения этих прав в генерируемом пакете должны быть согласованы с
соответствующим преобразованием в `generate.py`.

**Проверка изменений:** Генерируемые файлы пакетов зависят от `generate.py`: перед ручной правкой определите, не будет ли она перезаписана следующей генерацией. Проверяйте согласованность модуля ядра, userspace и LuCI с целевой версией OpenWrt; не считайте успешный workflow доказательством работы протокола на роутере.

**Типовые изменения:**

- Изменение процесса обновления upstream: редактируйте `generate.py`,
  учитывая режимы `tools`, `luci`, `kmod`, `all` и стадии генерации.
- Изменение сборочных зависимостей: согласуйте `amneziawg/Makefile`,
  `amneziawg-tools/Makefile` и `luci-proto-amneziawg/Makefile`.

**Источник истины:** `generate.py` создаёт содержимое пакетов из upstream
с последующими преобразованиями. Ручные изменения сгенерированных файлов
могут быть потеряны при обновлении; сначала определите стадию, на которой
нужно вносить правку.

## Сборка и установка

`openwrt-build.sh` теперь хранится в [openwrt-package-ci](https://github.com/karen07/openwrt-package-ci). Для локального запуска можно клонировать `openwrt-package-ci` рядом с этим репозиторием и временно сделать ссылку:

```sh
ln -s ../openwrt-package-ci/openwrt-build.sh ./openwrt-build.sh
```

После этого доступны те же три режима:

```text
install       определить параметры по SSH, собрать пакет и установить на роутер
build-router  определить target/arch по SSH, но использовать указанную версию OpenWrt
build-target  собрать по явно указанным version/target/subtarget/pkgarch
```

Поддерживаемые значения package:

```text
all
kmod-amneziawg
amneziawg-tools
luci-proto-amneziawg
```

### Установка на роутер

```sh
./openwrt-build.sh install all router
```

Скрипт:

1. подключается к роутеру по SSH;
1. читает `/etc/os-release`;
1. определяет `VERSION`, `OPENWRT_BOARD`, `OPENWRT_ARCH`;
1. скачивает подходящий OpenWrt SDK;
1. копирует локальные пакеты в SDK;
1. собирает выбранные пакеты;
1. копирует `.apk` на роутер;
1. устанавливает пакет через `apk add --allow-untrusted`.

Можно собрать и установить один пакет:

```sh
./openwrt-build.sh install kmod-amneziawg router
./openwrt-build.sh install amneziawg-tools router
./openwrt-build.sh install luci-proto-amneziawg router
```

Для чистой установки обычно лучше использовать:

```sh
./openwrt-build.sh install all router
```

### Сборка для роутера без установки

```sh
./openwrt-build.sh build-router all router 25.12.5
```

Скрипт возьмет `OPENWRT_BOARD` и `OPENWRT_ARCH` с роутера, но SDK скачает для указанной версии OpenWrt.

Сохранить результат в отдельную папку:

```sh
./openwrt-build.sh build-router all router 25.12.5 awgrelease
```

### Сборка с явными target/subtarget/pkgarch

```sh
./openwrt-build.sh build-target all 25.12.5 x86 64 x86_64 awgrelease
```

Этот режим удобен для CI и GitHub Actions, потому что не требует доступа к роутеру.

Формат:

```text
./openwrt-build.sh build-target <package> <version> <target> <subtarget> <pkgarch> [output-dir]
```

Пример для одного пакета:

```sh
./openwrt-build.sh build-target luci-proto-amneziawg 25.12.5 x86 64 x86_64 awgrelease
```

После локальной сборки временную ссылку можно удалить:

```sh
rm ./openwrt-build.sh
```

### Матрица GitHub Actions

`openwrt-matrix.py` из [openwrt-package-ci](https://github.com/karen07/openwrt-package-ci) генерирует matrix для OpenWrt targets/subtargets по данным с `downloads.openwrt.org`.

Формат:

```text
../openwrt-package-ci/openwrt-matrix.py <version> [include] [exclude]
```

`include` и `exclude` - это comma-separated patterns для `target` или `target/subtarget`.

Поддерживаются, например:

```text
*
all
x86
x86/*
x86/64
mediatek/filogic
x86/64,mediatek/filogic
microchipsw/*
```

Примеры:

```sh
../openwrt-package-ci/openwrt-matrix.py 25.12.5
../openwrt-package-ci/openwrt-matrix.py 25.12.5 'x86/*'
../openwrt-package-ci/openwrt-matrix.py 25.12.5 'x86/64,mediatek/filogic'
../openwrt-package-ci/openwrt-matrix.py 25.12.5 '*' 'microchipsw/lan969x'
../openwrt-package-ci/openwrt-matrix.py 25.12.5 'all' 'microchipsw/*' --pretty
```

То же самое можно задавать через options:

```sh
../openwrt-package-ci/openwrt-matrix.py 25.12.5 --include 'x86/64,mediatek/filogic' --exclude 'microchipsw/*' --pretty
```

Скрипт написан на Python standard library и не требует сторонних Python-зависимостей.

Он возвращает элементы вида:

```json
{
  "tag": "25.12.5",
  "target": "x86",
  "subtarget": "64",
  "board": "x86/64",
  "pkgarch": "x86_64"
}
```

Если задан `$GITHUB_OUTPUT`, скрипт дополнительно пишет туда `job-config=<json>`. Это поведение можно отключить флагом `--no-github-output`.

В GitHub Actions этот список используется для параллельной сборки `.apk` под разные OpenWrt targets.

### Процесс GitHub Actions

Workflow `.github/workflows/openwrt-build.yml` остается точкой входа этого репозитория и вызывает reusable workflow из [openwrt-package-ci](https://github.com/karen07/openwrt-package-ci).

Он запускается:

- по push тега вида `v*.*.*`;
- вручную через `workflow_dispatch`;
- из другого workflow через `workflow_call`.

Для ручного запуска можно выбрать:

| Параметр | Значение |
| --------- | ---------------------------------------------------------------------- |
| `version` | OpenWrt version, например `25.12.5`. |
| `package` | `all`, `kmod-amneziawg`, `amneziawg-tools` или `luci-proto-amneziawg`. |
| `include` | Include patterns для target/subtarget. По умолчанию: `*`. |
| `exclude` | Exclude patterns. По умолчанию: `microchipsw/lan969x`. |

### Артефакты релиза

GitHub Actions собирает `.apk` пакеты и прикладывает их к GitHub Release с тегом OpenWrt версии, например `v25.12.5`.

Формат имени release artifact:

```text
<package>_v<VERSION>_<OPENWRT_ARCH>_<TARGET>_<SUBTARGET>.apk
```

Примеры:

```text
kmod-amneziawg_v25.12.5_x86_64_x86_64.apk
amneziawg-tools_v25.12.5_aarch64_cortex-a53_mediatek_filogic.apk
luci-proto-amneziawg_v25.12.5_aarch64_cortex-a53_qualcommax_ipq807x.apk
```

В имени файла:

- `<VERSION>` - версия OpenWrt;
- `<OPENWRT_ARCH>` - значение `OPENWRT_ARCH` или package architecture;
- `<TARGET>` и `<SUBTARGET>` - OpenWrt target/subtarget, для которых собран пакет.

### Генерация из upstream-пакетов WireGuard

`generate.py` полностью формирует локальные каталоги `amneziawg-tools`, `luci-proto-amneziawg` и `amneziawg` из upstream-источников.

По умолчанию используются:

```text
OPENWRT_REPO=https://github.com/openwrt/openwrt.git
OPENWRT_REF=openwrt-25.12
LUCI_REPO=https://github.com/openwrt/luci.git
LUCI_REF=openwrt-25.12
AWG_LUCI_ICON_REPO=https://raw.githubusercontent.com/Slava-Shchipunov/awg-openwrt
AWG_LUCI_ICON_REF=master
```

Запуск:

```sh
./generate.py all
```

Только tools:

```sh
./generate.py tools
```

Только LuCI:

```sh
./generate.py luci
```

Только kernel package:

```sh
./generate.py kmod
```

Проверить, не вышла ли новая версия AmneziaWG tools или kernel module, ничего не обновляя:

```sh
./generate.py check
```

Версии AmneziaWG фиксируются в `generate.py` независимо:

```python
AWG_TOOLS_VERSION = "3.1.20260812"
AWG_KERNEL_VERSION = "3.1.20260906"
AWG_LUCI_VERSION = "3.1.0"
```

Если upstream версия tools или kernel module изменилась, `generate.py` останавливается и требует сначала вручную проверить изменения AWG и обновить соответствующую константу.

Генерацию можно остановить на любом промежуточном этапе. Это позволяет разложить обновление на отдельные небольшие Git-коммиты:

```sh
# 1. Чистая upstream WireGuard база. kmod-amneziawg отсутствует.
./generate.py all --vanilla-only
git add -A && git commit -m 'Import vanilla WireGuard packages'

# 2. Только переименование путей и файлов.
./generate.py all --rename-files-only
git add -A && git commit -m 'Rename WireGuard package paths to AmneziaWG'

# Старое имя опции оставлено как alias:
# ./generate.py all --rename-only

# 3. Плюс текстовые WireGuard/wg -> AmneziaWG/awg замены.
./generate.py all --rename-text-only
git add -A && git commit -m 'Rename WireGuard identifiers to AmneziaWG'

# 4. Полная генерация: AWG source/version, параметры, LuCI sections и fixes.
# Здесь впервые создаётся amneziawg/Makefile и добавляется amneziawg.svg.
./generate.py all
git add -A && git commit -m 'Add AmneziaWG-specific extensions'
```

То же самое можно задавать одной опцией `--stage`:

```sh
./generate.py all --stage vanilla
./generate.py all --stage files
./generate.py all --stage text
./generate.py all --stage full
```

Каждый режим строит целевое состояние заново из одной и той же upstream WireGuard базы, а не продолжает мутировать результат предыдущего запуска. Поэтому diff между соседними коммитами содержит только изменения соответствующего этапа. Промежуточные `vanilla`, `files` и `text` состояния предназначены прежде всего для review/diff и не обязаны собираться как полноценный AmneziaWG пакет.

`OPENWRT_REPO`, `OPENWRT_REF`, `LUCI_REPO`, `LUCI_REF`, `AWG_LUCI_ICON_REPO` и `AWG_LUCI_ICON_REF` можно переопределить через переменные окружения.

Сам `generate.py` делает sparse checkout только нужных upstream директорий, а не клонирует весь OpenWrt и LuCI целиком.

### Установка готовых `.apk`

Если пакеты уже собраны в GitHub Releases, их можно скачать и установить вручную на роутере.

Обычно проще держать все три `.apk` рядом и передать их в `apk` одной командой:

```sh
apk add --allow-untrusted ./kmod-amneziawg_*.apk ./amneziawg-tools_*.apk ./luci-proto-amneziawg_*.apk
```

Так `apk` видит все локальные пакеты одновременно и может обработать зависимости между ними.

## Что входит в проект

```text
amneziawg-openwrt-package/
|-- .github/workflows/openwrt-build.yml
|-- openwrt-build.env
|-- generate.py
|-- amneziawg/
|-- amneziawg-tools/
`-- luci-proto-amneziawg/
```

Основные компоненты:

| Путь | Назначение |
| ----------------------- | ------------------------------------------------------- |
| `openwrt-build.env` | Параметры пакетов для общего CI. |
| `.github/workflows/openwrt-build.yml` | Caller reusable workflow из `openwrt-package-ci`. |
| `generate.py` | Генерация целевого состояния пакетов из upstream-источников по стадиям `vanilla`, `files`, `text`, `full`. |
| `amneziawg/` | Сгенерированный OpenWrt kernel package для модуля AmneziaWG. |
| `amneziawg-tools/` | Userspace tools и netifd proto script. |
| `luci-proto-amneziawg/` | LuCI protocol package для настройки AmneziaWG. |

Пакеты:

- `kmod-amneziawg` - kernel module package для AmneziaWG.
- `amneziawg-tools` - userspace tools и netifd protocol script.
- `luci-proto-amneziawg` - LuCI интерфейс для настройки AmneziaWG.

## Чем этот проект отличается

### 1. Автопатч исходного WireGuard

`amneziawg-tools`, `luci-proto-amneziawg` и `kmod-amneziawg` не ведутся как ручной форк. Их целевое состояние полностью генерируется через `generate.py`:

1. из upstream OpenWrt берется ванильный пакет `wireguard-tools`;
1. из upstream LuCI берется ванильный пакет `luci-proto-wireguard`;
1. WireGuard пути, имена файлов и идентификаторы переименовываются в AmneziaWG;
1. добавляются только AmneziaWG специфичные параметры и небольшие необходимые изменения;
1. на финальном этапе генерируется `amneziawg/Makefile` с версией из `AWG_KERNEL_VERSION`;
1. иконка LuCI `amneziawg.svg` берётся из `Slava-Shchipunov/awg-openwrt`.

Это упрощает обновление под новые версии OpenWrt и LuCI. Вместо ручного переноса больших кусков кода можно заново взять чистую upstream базу и применить проектный патч.

### 2. Отдельный пакет модуля ядра OpenWrt

`kmod-amneziawg` оформлен как отдельный OpenWrt kernel package. Его `Makefile` не является отдельным ручным source-файлом: `generate.py` создаёт его на стадии `full`, подставляя `AWG_KERNEL_VERSION`. На стадиях `vanilla`, `files` и `text` каталог `amneziawg/` отсутствует, поскольку ванильного WireGuard-пакета, из которого его можно было бы получить rename-ом, нет.

### 3. Нормальная цепочка зависимостей пакетов

Зависимости задаются на уровне OpenWrt пакетов, а не только логикой install скрипта.

```text
luci-proto-amneziawg
`-- depends on amneziawg-tools
    `-- depends on kmod-amneziawg
```

Это важно: LuCI пакет не должен устанавливаться как независимая оболочка без backend/tools, а tools не должны устанавливаться без kernel module.

При установке всех пакетов порядок выглядит так:

1. `kmod-amneziawg`
1. `amneziawg-tools`
1. `luci-proto-amneziawg`

### 4. Поддержка готовых сборок и локальной разработки

Проект рассчитан на два сценария:

- готовые `.apk` сборки через GitHub Actions и GitHub Releases;
- локальная сборка из текущего рабочего дерева через OpenWrt SDK.

Это удобно для разработки: можно менять локальные файлы пакетов и сразу собирать их под конкретный роутер или target/subtarget.

### 5. Сборки OpenWrt 25.12+ на основе APK

Проект ориентирован на новые версии OpenWrt с `.apk` пакетами.

Старые OpenWrt версии с `.ipk` и opkg не являются целью этого проекта.

## Что добавляется поверх WireGuard

В `amneziawg-tools` и `luci-proto-amneziawg` добавляются AmneziaWG специфичные параметры.

Базовые параметры маскировки:

```text
Jc, Jmin, Jmax
S1, S2, S3, S4
H1, H2, H3, H4
I1, I2, I3, I4, I5
```

Параметры AWG 3.0:

```text
HeaderProtectionKey
ContentPaddingAddition
RekeyAfterTime
RekeyTimeout
RejectAfterTime
KeepaliveTimeout
MaxHandshakeAttempts
```

Параметры AWG 3.1:

```text
RandomTrailers
DisableCookies
```

В `amneziawg-tools v3.1.20260812` новые range-параметры хранятся как `u16_range_t`, поэтому используемый диапазон значений - `0-65535`:

```text
ContentPaddingAddition  0-65535 bytes
RekeyAfterTime          0-65535 seconds
RekeyTimeout            0-65535 seconds
RejectAfterTime         0-65535 seconds
KeepaliveTimeout        0-65535 seconds
MaxHandshakeAttempts    0-65535 attempts
PersistentKeepalive     0-65535 seconds
```

В UCI новые CamelCase имена преобразуются в `snake_case`, например:

```text
HeaderProtectionKey -> awg_header_protection_key
ContentPaddingAddition -> awg_content_padding_addition
RandomTrailers -> awg_random_trailers
```

В AWG 3.1 `PersistentKeepalive` может быть как одним значением, так и диапазоном:

```text
25
20-30
```

Поэтому netifd/LuCI передают это поле как строковое значение, а `status.js` не приводит его к числу. Валидация самого диапазона остается за `awg`.

## Для кого этот проект

Проект подходит, если нужно:

- собирать AmneziaWG под конкретные OpenWrt targets;
- получать воспроизводимые `.apk` через OpenWrt SDK;
- иметь LuCI интеграцию для AmneziaWG;
- обновлять userspace и LuCI часть от свежей WireGuard базы;
- использовать проект как dev-friendly пакетную базу, а не только как набор готовых бинарников.

## Не цели проекта

Проект не пытается:

- поддерживать старые OpenWrt версии с `.ipk` и opkg;
- быть универсальным установщиком для всех возможных прошивок;
- автоматически править firewall, routing policy и пользовательскую конфигурацию роутера;
- хранить большой ручной форк LuCI/WireGuard без связи с upstream.

## Краткая памятка

Этот репозиторий - пакетная база AmneziaWG для OpenWrt 25.12+:

- `kmod-amneziawg` - модуль ядра;
- `amneziawg-tools` - userspace и netifd интеграция;
- `luci-proto-amneziawg` - LuCI UI;
- `generate.py` - генератор пакетов из ванильной WireGuard/OpenWrt базы;
- `openwrt-build.env` - параметры пакетов для общей CI-инфраструктуры;
- [openwrt-package-ci](https://github.com/karen07/openwrt-package-ci) - общий SDK build helper, matrix generator и reusable workflow.

## Лицензия

Проектные скрипты этого репозитория распространяются под GNU Affero General Public License v3.0. Подробности см. в файле [LICENSE](LICENSE). Файлы, полученные из OpenWrt, LuCI и других upstream-проектов, сохраняют соответствующие upstream copyright и license notices.
