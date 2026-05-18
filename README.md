# AmneziaWG OpenWrt

[![Build OpenWrt AmneziaWG packages](https://github.com/karen07/amneziawg-openwrt-package/actions/workflows/openwrt-build.yml/badge.svg)](https://github.com/karen07/amneziawg-openwrt-package/actions/workflows/openwrt-build.yml)

OpenWrt пакеты для AmneziaWG: модуль ядра, userspace tools и LuCI протокол.

Главная идея проекта - не поддерживать большой ручной форк WireGuard пакетов, а генерировать AmneziaWG пакеты из чистой upstream базы. Ванильные OpenWrt и LuCI WireGuard пакеты берутся как источник, после чего `generate.py` последовательно переименовывает их и накладывает только AmneziaWG-специфичные изменения.

## Что входит в проект

```text
amneziawg-openwrt-package/
|-- openwrt-build.sh
|-- openwrt-matrix.py
|-- generate.py
|-- kmod-amneziawg/
|-- amneziawg-tools/
`-- luci-proto-amneziawg/
```

Основные компоненты:

| Путь | Назначение |
| ----------------------- | ------------------------------------------------------- |
| `openwrt-build.sh` | Локальная сборка и установка пакетов через OpenWrt SDK. |
| `openwrt-matrix.py` | Генерация GitHub Actions matrix по OpenWrt targets. |
| `generate.py` | Генерация целевого состояния пакетов из upstream-источников по стадиям `vanilla`, `files`, `text`, `full`. |
| `kmod-amneziawg/` | Сгенерированный OpenWrt kernel package для модуля AmneziaWG. |
| `amneziawg-tools/` | Userspace tools и netifd proto script. |
| `luci-proto-amneziawg/` | LuCI protocol package для настройки AmneziaWG. |

Пакеты:

- `kmod-amneziawg` - kernel module package для AmneziaWG.
- `amneziawg-tools` - userspace tools и netifd protocol script.
- `luci-proto-amneziawg` - LuCI интерфейс для настройки AmneziaWG.

## Чем этот проект отличается

### 1. Автопатч от ванильной WireGuard базы

`amneziawg-tools`, `luci-proto-amneziawg` и `kmod-amneziawg` не ведутся как ручной форк. Их целевое состояние полностью генерируется через `generate.py`:

1. из upstream OpenWrt берется ванильный пакет `wireguard-tools`;
1. из upstream LuCI берется ванильный пакет `luci-proto-wireguard`;
1. WireGuard пути, имена файлов и идентификаторы переименовываются в AmneziaWG;
1. добавляются только AmneziaWG специфичные параметры и небольшие необходимые изменения;
1. на финальном этапе генерируется `kmod-amneziawg/Makefile` с версией из `AWG_KERNEL_VERSION`;
1. иконка LuCI `amneziawg.svg` берётся из `Slava-Shchipunov/awg-openwrt`.

Это упрощает обновление под новые версии OpenWrt и LuCI. Вместо ручного переноса больших кусков кода можно заново взять чистую upstream базу и применить проектный патч.

### 2. Отдельный OpenWrt пакет для kernel module

`kmod-amneziawg` оформлен как отдельный OpenWrt kernel package. Его `Makefile` не является отдельным ручным source-файлом: `generate.py` создаёт его на стадии `full`, подставляя `AWG_KERNEL_VERSION`. На стадиях `vanilla`, `files` и `text` каталог `kmod-amneziawg/` отсутствует, поскольку ванильного WireGuard-пакета, из которого его можно было бы получить rename-ом, нет.

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

### 5. OpenWrt 25.12+ и apk based сборки

Проект ориентирован на новые версии OpenWrt с `.apk` пакетами.

Старые OpenWrt версии с `.ipk` и opkg не являются целью этого проекта.

## Сборка и установка

`openwrt-build.sh` умеет работать в трех режимах:

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

## Установить на роутер

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

## Собрать под роутер, но не устанавливать

```sh
./openwrt-build.sh build-router all router 25.12.5
```

Скрипт возьмет `OPENWRT_BOARD` и `OPENWRT_ARCH` с роутера, но SDK скачает для указанной версии OpenWrt.

Сохранить результат в отдельную папку:

```sh
./openwrt-build.sh build-router all router 25.12.5 awgrelease
```

## Собрать по явному target/subtarget/pkgarch

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

## GitHub Actions matrix

`openwrt-matrix.py` генерирует matrix для OpenWrt targets/subtargets по данным с `downloads.openwrt.org`.

Формат:

```text
./openwrt-matrix.py <version> [include] [exclude]
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
./openwrt-matrix.py 25.12.5
./openwrt-matrix.py 25.12.5 'x86/*'
./openwrt-matrix.py 25.12.5 'x86/64,mediatek/filogic'
./openwrt-matrix.py 25.12.5 '*' 'microchipsw/lan969x'
./openwrt-matrix.py 25.12.5 'all' 'microchipsw/*' --pretty
```

То же самое можно задавать через options:

```sh
./openwrt-matrix.py 25.12.5 --include 'x86/64,mediatek/filogic' --exclude 'microchipsw/*' --pretty
```

Скрипт написан на Python standard library и не требует npm зависимостей.

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

## GitHub Actions workflow

Workflow `openwrt-build.yml` запускается:

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

Внутри workflow сначала генерируется matrix через `openwrt-matrix.py`, потом для каждого target/subtarget вызывается:

```sh
./openwrt-build.sh build-target <package> <version> <target> <subtarget> <pkgarch> awgrelease
```

## Release artifacts

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

## Генерация из upstream WireGuard пакетов

`generate.py` полностью формирует локальные `amneziawg-tools`, `luci-proto-amneziawg` и `kmod-amneziawg` из upstream-источников.

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
AWG_KERNEL_VERSION = "3.1.20260812"
AWG_LUCI_VERSION = "3.1.20260812"
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
# Здесь впервые создаётся kmod-amneziawg/Makefile и добавляется amneziawg.svg.
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

## Установка готовых `.apk`

Если пакеты уже собраны в GitHub Releases, их можно скачать и установить вручную на роутере.

Обычно проще держать все три `.apk` рядом и передать их в `apk` одной командой:

```sh
apk add --allow-untrusted ./kmod-amneziawg_*.apk ./amneziawg-tools_*.apk ./luci-proto-amneziawg_*.apk
```

Так `apk` видит все локальные пакеты одновременно и может обработать зависимости между ними.

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

## Коротко

Этот репозиторий - пакетная база AmneziaWG для OpenWrt 25.12+:

- `kmod-amneziawg` - модуль ядра;
- `amneziawg-tools` - userspace и netifd интеграция;
- `luci-proto-amneziawg` - LuCI UI;
- `generate.py` - генератор пакетов из ванильной WireGuard/OpenWrt базы;
- `openwrt-build.sh` - локальная SDK сборка и установка;
- `openwrt-matrix.py` - matrix для GitHub Actions.

## Лицензия

Проектные скрипты этого репозитория распространяются под GNU Affero General Public License v3.0. Файлы, полученные из OpenWrt, LuCI и других upstream-проектов, сохраняют соответствующие upstream copyright и license notices.
