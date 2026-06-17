#!/usr/bin/env -S PYTHONPATH=../../../tools/extract-utils python3
#
# SPDX-FileCopyrightText: 2024 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#

from extract_utils.fixups_blob import (
    blob_fixup,
    blob_fixups_user_type,
)
from extract_utils.fixups_lib import (
    lib_fixups,
    lib_fixups_user_type,
)
from extract_utils.main import (
    ExtractUtils,
    ExtractUtilsModule,
)

namespace_imports = [
    'device/oneplus/sm8550-common',
    'hardware/oplus',
    'hardware/pixelworks/interfaces',
    'hardware/qcom-caf/sm8550',
    'hardware/qcom-caf/wlan',
    'vendor/qcom/opensource/commonsys/display',
    'vendor/qcom/opensource/commonsys-intf/display',
    'vendor/qcom/opensource/dataservices',
]


def lib_fixup_vendor_suffix(lib: str, partition: str, *args, **kwargs):
    return f'{lib}_{partition}' if partition == 'vendor' else None


lib_fixups: lib_fixups_user_type = {
    **lib_fixups,
    (
        'com.qualcomm.qti.dpm.api@1.0',
        'libQnnCpu',
        'libQnnHtp',
        'libQnnHtpPrepare',
        'libQnnHtpV73Stub',
        'libpwirisfeature',
        'libpwirishalwrapper',
        'vendor.oplus.hardware.communicationcenter-V2-ndk',
        'vendor.qti.diaghal@1.0',
        'vendor.qti.hardware.dpmservice@1.0',
        'vendor.qti.hardware.qccsyshal@1.0',
        'vendor.qti.hardware.qccsyshal@1.1',
        'vendor.qti.hardware.qccsyshal@1.2',
        'vendor.qti.hardware.qccvndhal@1.0',
        'vendor.qti.hardware.wifidisplaysession@1.0',
        'vendor.qti.imsrtpservice@3.0',
        'vendor.qti.imsrtpservice@3.1',
    ): lib_fixup_vendor_suffix,
}

blob_fixups: blob_fixups_user_type = {
    (
        'odm/bin/touchDaemon',
        'odm/bin/hw/vendor.oplus.hardware.biometrics.fingerprint@2.1-service_uff',
        'vendor/bin/poweropt-service',
        'vendor/lib64/libaodoptfeature.so',
        'vendor/lib64/libapengine.so',
        'vendor/lib64/libdpps.so',
        'vendor/lib64/liblearningmodule.so',
        'vendor/lib64/libpowercore.so',
        'vendor/lib64/libpsmoptfeature.so',
        'vendor/lib64/libsnapdragoncolor-manager.so',
        'vendor/lib64/libstandbyfeature.so',
        'vendor/lib64/libvideooptfeature.so',
    ): blob_fixup()
        .replace_needed('libtinyxml2.so', 'libtinyxml2-v34.so'),
    'odm/bin/hw/vendor.oplus.hardware.biometrics.fingerprint@2.1-service_uff': blob_fixup()
        .add_needed('libshims_aidl_fingerprint_v2.oplus.so'),
    'odm/bin/hw/vendor.oplus.hardware.charger-V10-service': blob_fixup()
        .add_needed('libbase_shim.so'),
    'odm/etc/init/init.network.rc': blob_fixup()
        .regex_replace(r'/\* (Huo\.Chen@SYSTEM\.RF, 2024/09/06, Add for ICC) \*/', r'# \1'),
    'product/etc/sysconfig/com.android.hotwordenrollment.common.util.xml': blob_fixup()
        .regex_replace('/my_product', '/product'),
    'system_ext/bin/horae': blob_fixup()
        .replace_needed('libprotobuf-cpp-lite.so', 'libprotobuf-cpp-lite-21.7.so'),
    'system_ext/lib64/libwfdnative.so': blob_fixup()
        .add_needed('libinput_shim.so'),
    'system_ext/lib64/vendor.qti.hardware.qccsyshal@1.2-halimpl.so': blob_fixup()
        .replace_needed('libprotobuf-cpp-full.so', 'libprotobuf-cpp-full-21.7.so'),
    'vendor/bin/hw/android.hardware.contexthub-service.qmi': blob_fixup()
        .replace_needed('libbase.so', 'libbase-v33.so'),
    ('vendor/bin/hw/android.hardware.security.keymint-service-qti', 'vendor/lib64/libqtikeymint.so'): blob_fixup()
        .add_needed('android.hardware.security.rkp-V3-ndk.so'),
    'vendor/etc/media_codecs_kalama.xml': blob_fixup()
        .regex_replace('.*media_codecs_(google_audio|google_c2|google_telephony|google_video|vendor_audio).*\n', '')
        .regex_replace('</MediaCodecs>','    <Include href="media_codecs_dolby_audio.xml" />')
        .add_line_if_missing('</MediaCodecs>'),
    'vendor/etc/seccomp_policy/qwesd@2.0.policy': blob_fixup()
        .add_line_if_missing('pipe2: 1'),
    'vendor/lib64/libqcodec2_core.so': blob_fixup()
        .add_needed('libcodec2_shim.so'),
    'vendor/lib64/vendor.libdpmframework.so': blob_fixup()
        .add_needed('libhidlbase_shim.so'),
    # APS turbo fix: on the port, the camera app's classloader namespace cannot dlopen the /odm
    # ArcSoft/QNN helper libs (couple-HDR, turbo, QNN HTP), which gates the DSP/QNN path so turbo
    # can't run. Exposing them as vendor public libraries lets the app namespace resolve them.
    'vendor/etc/public.libraries.txt': blob_fixup()
        .add_line_if_missing('libarcsoft_hdr_couple_api.so')
        .add_line_if_missing('libarcsoft_high_dynamic_range_couple.so')
        .add_line_if_missing('libarcsoft_smart_denoise.so')
        .add_line_if_missing('libarcsoft_turbo_hdr_raw.so')
        .add_line_if_missing('libarcsoft_turbo_raw.so')
        .add_line_if_missing('libarcsoft_qnnhtp.so')
        .add_line_if_missing('libQnnHtp.so')
        .add_line_if_missing('libQnnSystem.so')
        .add_line_if_missing('libQnnHtpV79Stub.so')
        .add_line_if_missing('libQnnGpu.so')
        .add_line_if_missing('libQnnHtpStub.so')
        # libapsfixup.so is a /odm lib that libAlgoProcess now DT_NEEDEDs; the camera namespace
        # can't resolve /odm libs by name, so expose it as a public library too.
        .add_line_if_missing('libapsfixup.so'),
    'vendor/etc/seccomp_policy/gnss@2.0-qsap-location.policy': blob_fixup()
        .add_line_if_missing('sched_get_priority_min: 1')
        .add_line_if_missing('sched_get_priority_max: 1'),
    'vendor/lib64/hw/android.hardware.bluetooth.audio_sw.so': blob_fixup()
        .replace_needed('android.media.audio.common.types-V4-ndk.so', 'android.media.audio.common.types-V3-ndk.so'),
    (
        'vendor/lib64/hw/libaudiocorehal.qti.so',
        'vendor/lib64/soundfx/libbundleaidl.so',
    ): blob_fixup()
        .replace_needed('libaudio_aidl_conversion_common_ndk.so', 'libaudio_aidl_conversion_common_ndk_prebuilt.so'),
    'vendor/lib64/android.hardware.bluetooth.audio-impl_prebuilt.so': blob_fixup()
        .replace_needed('libbluetooth_audio_session_aidl.so', 'libbluetooth_audio_session_aidl_prebuilt.so'),
    (
        'vendor/lib64/libVoiceSdk.so',
        'vendor/lib64/libcapiv2uvvendor.so',
        'vendor/lib64/liblistensoundmodel2vendor.so',
    ): blob_fixup()
        .replace_needed('libtensorflowlite_c.so', 'libtensorflowlite_c_vendor.so'),
    (
        'vendor/lib64/libapengine.so',
        'vendor/lib64/libqti-perfd.so',
    ): blob_fixup()
        .replace_needed('vendor.qti.hardware.display.config-V5-ndk.so', 'vendor.qti.hardware.display.config-V12-ndk.so'),
    'vendor/lib64/libaudioserviceexampleimpl.so': blob_fixup()
        .add_needed('libaudioutils_shim.so')
        .replace_needed('android.hardware.bluetooth.audio-impl.so', 'android.hardware.bluetooth.audio-impl_prebuilt.so')
        .replace_needed('libaudio_aidl_conversion_common_ndk.so', 'libaudio_aidl_conversion_common_ndk_prebuilt.so')
        .replace_needed('libbluetooth_audio_session_aidl.so', 'libbluetooth_audio_session_aidl_prebuilt.so'),
    (
        'vendor/lib64/libcwb_qcom_aidl.so',
        'vendor/lib64/libhwcsensor.so',
        'vendor/lib64/libsdmclient.so',
    ): blob_fixup()
        .replace_needed('vendor.qti.hardware.display.config-V11-ndk.so', 'vendor.qti.hardware.display.config-V12-ndk.so'),
    (
        'vendor/lib64/libloc_api_v02.so',
        'vendor/lib64/libloc_core.so',
    ): blob_fixup()
        .add_needed('libbase.so'),
    'vendor/lib64/libwfdmmsrc_proprietary.so': blob_fixup()
        .replace_needed('android.media.audio.common.types-V2-ndk.so', 'android.media.audio.common.types-V3-ndk.so'),
    'vendor/etc/media_codecs_sun.xml': blob_fixup()
        #FIX HDR ENCODER
        .regex_replace(
            r'<!--\s*<MediaCodec name="c2\.qti\.dv\.encoder" type="video/dolby-vision">',
            r'<MediaCodec name="c2.qti.dv.encoder" type="video/dolby-vision">'
        )
        .regex_replace(
            r'(<Limit name="performance-point-7680x4320" value="30" />\s*)</MediaCodec>\s*-->',
            r'\1    <Feature name="profile-and-level" value="256-8" />\n'
            r'            <Feature name="profile-and-level" value="256-256" />\n'
            r'            <Feature name="profile-and-level" value="256-1024" />\n'
            r'        </MediaCodec>'
        )
        #FIX HDR DECODER
        .regex_replace(
            r'<!--\s*<MediaCodec name="c2\.qti\.dv\.decoder" type="video/dolby-vision" >',
            r'<MediaCodec name="c2.qti.dv.decoder" type="video/dolby-vision" >'
        )
        .regex_replace(
            r'(<Limit name="performance-point-8192x4320" value="48" />\s*)</MediaCodec>',
            r'\1    <Feature name="profile-and-level" value="256-8" />\n'
            r'            <Feature name="profile-and-level" value="256-256" />\n'
            r'            <Feature name="profile-and-level" value="256-1024" />\n'
            r'        </MediaCodec>'
        )
        #FIX HDR DECODER SECURE
        .regex_replace(
            r'(<Limit name="performance-point-4096x2304" value="120" />\s*)</MediaCodec>\s*-->',
            r'\1    <Feature name="profile-and-level" value="256-8" />\n'
            r'            <Feature name="profile-and-level" value="256-256" />\n'
            r'            <Feature name="profile-and-level" value="256-1024" />\n'
            r'        </MediaCodec>'
        ),
}  # fmt: skip

module = ExtractUtilsModule(
    'sm8550-common',
    'oneplus',
    blob_fixups=blob_fixups,
    lib_fixups=lib_fixups,
    namespace_imports=namespace_imports,
)

if __name__ == '__main__':
    utils = ExtractUtils.device(module)
    utils.run()
