from conans import ConanFile, CMake, tools
from conans.tools import os_info, SystemPackageTool


class OGREConan(ConanFile):
    name = "OGRE"
    version = "2.2.5"
    license = "MIT"
    url = "https://github.com/AnotherFoxGuy/conan-OGRE"
    description = "scene-oriented, flexible 3D engine written in C++"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def system_requirements(self):
        if os_info.is_linux:
            if os_info.with_apt:
                installer = SystemPackageTool()
                installer.install("xorg-dev")
                installer.install("libfreeimage-dev")
                installer.install("libgl1-mesa-dev")
                installer.install("libglu1-mesa-dev")
                installer.install("nvidia-cg-toolkit")
                installer.install("libopenal-dev")
                installer.install("libx11-dev")
                installer.install("libxt-dev")
                installer.install("libxaw7-dev")
                installer.install("libpugixml-dev")
                installer.install("libzzip-dev")

    def requirements(self):
        if os_info.is_windows:
            self.requires.add('zlib/[1.x]')
            self.requires.add('zziplib/[0.13.x]')
            self.requires.add('freetype/[2.x]')
            self.requires.add('freeimage/[3.x]@AnotherFoxGuy/stable')
            self.requires.add('pugixml/[1.x]')

    def source(self):
        git = tools.Git()
        git.clone("https://github.com/OGRECave/ogre-next.git", "v2.2.5")
        git.run("submodule update --init --recursive")
        if os_info.is_windows:
            tools.replace_in_file("Components/Overlay/CMakeLists.txt", '${FREETYPE_LIBRARIES}', "CONAN_PKG::freetype")
            tools.replace_in_file("CMakeLists.txt", 'FreeImage_FOUND', 'TRUE')
            tools.replace_in_file("OgreMain/CMakeLists.txt", '${FreeImage_LIBRARIES}',
                                  'CONAN_PKG::freeimage')

        tools.replace_in_file("CMakeLists.txt", "# Include necessary submodules", '''
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)''')

        tools.replace_in_file("CMake/Packages/FindFreeImage.cmake",
                              "set(FreeImage_LIBRARY_NAMES freeimage freeimageLib FreeImage FreeImageLib)",
                              "set(FreeImage_LIBRARY_NAMES freeimage freeimageLib FreeImage FreeImageLib libFreeImage)")

        tools.replace_in_file("CMake/Packages/FindZZip.cmake",
                              "set(ZZip_LIBRARY_NAMES zziplib zzip)",
                              "set(ZZip_LIBRARY_NAMES zziplib zzip zzip-0 libzziplib)")

        tools.replace_in_file("CMake/Dependencies.cmake",
                              '''set(OGRE_DEPENDENCIES_DIR "" CACHE PATH "Path to prebuilt OGRE dependencies")''',
                              '''set(OGRE_DEPENDENCIES_DIR ${CMAKE_PREFIX_PATH})''')

        tools.replace_in_file("CMake/Utils/FindPkgMacros.cmake",
                              'set(${PREFIX} optimized ${${PREFIX}_REL} debug ${${PREFIX}_DBG})',
                              'set(${PREFIX} ${${PREFIX}_REL} ${${PREFIX}_DBG})')

        tools.replace_in_file("CMakeLists.txt", "# Set up the basic build environment", '''
find_library(ZLIB_LIBRARY NAMES zlib zlib_d PATH_SUFFIXES lib)
find_library(FREETYPE_LIBRARY NAMES freetype freetype_d PATH_SUFFIXES lib) ''')

    def build(self):
        ogre_cmake_args = {
            'OGRE_BUILD_DEPENDENCIES':                  'OFF',
            'OGRE_USE_BOOST':                           '0',
            'OGRE_BUILD_COMPONENT_HLMS_PBS':            'ON',
            'OGRE_BUILD_COMPONENT_HLMS_UNLI':           'ON',
            'OGRE_BUILD_COMPONENT_HLMS_UNLIT':          'ON',
            'OGRE_BUILD_COMPONENT_MESHLODGENERATOR':    'ON',
            'OGRE_BUILD_COMPONENT_OVERLAY':             'ON',
            'OGRE_BUILD_COMPONENT_PAGING':              'ON',
            'OGRE_BUILD_COMPONENT_PLANAR_REFLECTIONS':  'ON',
            'OGRE_BUILD_COMPONENT_PROPERTY':            'ON',
            'OGRE_BUILD_COMPONENT_RTSHADERSYSTEM':      'ON',
            'OGRE_BUILD_COMPONENT_SCENE_FORMAT':        'ON',
            'OGRE_BUILD_COMPONENT_TERRAIN':             'ON',
            'OGRE_BUILD_COMPONENT_VOLUME':              'ON',
            'OGRE_BUILD_PLUGIN_PFX':                    'ON',
            'OGRE_BUILD_RENDERSYSTEM_GL3PLUS':          'ON',
            'OGRE_BUILD_RENDERSYSTEM_VULKAN':           'ON',
            'OGRE_BUILD_SAMPLES2':                      'OFF',
            'OGRE_BUILD_TESTS':                         'OFF',
            'OGRE_BUILD_TOOLS':                         'ON',
            'OGRE_CONFIG_ENABLE_JSON':                  'ON',
            'OGRE_CONFIG_ENABLE_QUAD_BUFFER':           'OFF',
            'OGRE_CONFIG_THREADS':                      '2',
            'OGRE_CONFIG_THREAD_PROVIDER':              'std',
            'OGRE_INSTALL_DOCS':                        'OFF',
            'OGRE_INSTALL_SAMPLES':                     'OFF',
            'OGRE_INSTALL_TOOLS':                       'ON',
            'OGRE_INSTALL_PDB':                         'OFF',  
            'OGRE_RESOURCEMANAGER_STRICT':              '0',
            'OGRE_BUILD_COMPONENT_OVERLAY_IMGUI':       'ON',   
            'OGRE_BUILD_COMPONENT_CSHARP':              'OFF',  
            'OGRE_BUILD_COMPONENT_JAVA':                'OFF',  
            'OGRE_BUILD_COMPONENT_PYTHON':              'OFF',  
            'OGRE_BUILD_PLUGIN_STBI':                   'OFF',  
            'OGRE_BUILD_COMPONENT_BITES':               'ON',   
        }  

        cmake = CMake(self)
        for k,v in ogre_cmake_args:
            cmake.definitions[k] = v

        if os_info.is_windows:
            cmake.definitions['CMAKE_CXX_FLAGS'] = '-D_OGRE_FILESYSTEM_ARCHIVE_UNICODE'
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.includedirs = ['include',
                                     'include/OGRE',
                                     'include/OGRE/Bites',
                                     'include/OGRE/HLMS',
                                     'include/OGRE/MeshLodGenerator',
                                     'include/OGRE/Overlay',
                                     'include/OGRE/Paging',
                                     'include/OGRE/Plugins',
                                     'include/OGRE/Property',
                                     'include/OGRE/RenderSystems',
                                     'include/OGRE/RTShaderSystem',
                                     'include/OGRE/Terrain',
                                     'include/OGRE/Threading',
                                     'include/OGRE/Volume'
                                     ]
        self.cpp_info.libs = tools.collect_libs(self)
