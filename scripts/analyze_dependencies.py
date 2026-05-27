#!/usr/bin/env python3
"""
OpenCog Dependency Graph Analyzer

This script parses all CMakeLists.txt files in the OpenCog repository to:
1. Extract FIND_PACKAGE directives
2. Build a complete dependency graph
3. Identify internal vs external dependencies
4. Generate dependency tiers for build ordering
5. Output machine-readable dependency data (JSON/YAML)
"""

import os
import re
import json
import yaml
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field, asdict
from collections import defaultdict


@dataclass
class Dependency:
    """Represents a package dependency"""
    name: str
    version: Optional[str] = None
    required: bool = True
    config_mode: bool = False
    
    def to_dict(self):
        return {
            'name': self.name,
            'version': self.version,
            'required': self.required,
            'config_mode': self.config_mode
        }


@dataclass 
class Package:
    """Represents an OpenCog package"""
    name: str
    path: str
    has_cmake: bool = False
    cmake_version: Optional[str] = None
    project_version: Optional[str] = None
    dependencies: List[Dependency] = field(default_factory=list)
    tier: int = -1  # -1 means not yet assigned
    
    def to_dict(self):
        return {
            'name': self.name,
            'path': self.path,
            'has_cmake': self.has_cmake,
            'cmake_version': self.cmake_version,
            'project_version': self.project_version,
            'dependencies': [d.to_dict() for d in self.dependencies],
            'tier': self.tier
        }


# Known OpenCog internal packages mapped to their canonical names
OPENCOG_PACKAGES = {
    # Name variations -> canonical name
    'cogutil': 'cogutil',
    'CogUtil': 'cogutil',
    'atomspace': 'atomspace',
    'AtomSpace': 'atomspace',
    'atomspace-rocks': 'atomspace-rocks',
    'AtomSpaceRocks': 'atomspace-rocks',
    'atomspace-storage': 'atomspace-storage',
    'AtomSpaceStorage': 'atomspace-storage',
    'atomspace-pgres': 'atomspace-pgres',
    'AtomSpacePGres': 'atomspace-pgres',
    'atomspace-cog': 'atomspace-cog',
    'AtomSpaceCog': 'atomspace-cog',
    'cogserver': 'cogserver',
    'CogServer': 'cogserver',
    'attention': 'attention',
    'Attention': 'attention',
    'attentionbank': 'attention',
    'AttentionBank': 'attention',
    'unify': 'unify',
    'Unify': 'unify',
    'ure': 'ure',
    'URE': 'ure',
    'pln': 'pln',
    'PLN': 'pln',
    'miner': 'miner',
    'Miner': 'miner',
    'spacetime': 'spacetime',
    'SpaceTime': 'spacetime',
    'lg-atomese': 'lg-atomese',
    'LGAtomese': 'lg-atomese',
    'link-grammar': 'link-grammar',
    'LinkGrammar': 'link-grammar',
    'moses': 'moses',
    'MOSES': 'moses',
    'asmoses': 'asmoses',
    'ASMoses': 'asmoses',
    'opencog': 'opencog',
    'OpenCog': 'opencog',
    'vision': 'vision',
    'Vision': 'vision',
    'perception': 'perception',
    'Perception': 'perception',
    'sensory': 'sensory',
    'Sensory': 'sensory',
    'learn': 'learn',
    'Learn': 'learn',
    'generate': 'generate',
    'Generate': 'generate',
    'benchmark': 'benchmark',
    'Benchmark': 'benchmark',
    'visualization': 'visualization',
    'Visualization': 'visualization',
    'cheminformatics': 'cheminformatics',
    'Cheminformatics': 'cheminformatics',
    'agi-bio': 'agi-bio',
    'AgiBio': 'agi-bio',
    'matrix': 'matrix',
    'Matrix': 'matrix',
    'pattern-index': 'pattern-index',
    'PatternIndex': 'pattern-index',
    'dimensional-embedding': 'dimensional-embedding',
    'DimensionalEmbedding': 'dimensional-embedding',
    'TinyCog': 'TinyCog',
    'ghost_bridge': 'ghost_bridge',
    'GhostBridge': 'ghost_bridge',
    'relex': 'relex',
    'RelEx': 'relex',
    'motor': 'motor',
    'Motor': 'motor',
    'atomspace-agents': 'atomspace-agents',
    'AtomSpaceAgents': 'atomspace-agents',
    'atomspace-dht': 'atomspace-dht',
    'AtomSpaceDHT': 'atomspace-dht',
    'atomspace-ipfs': 'atomspace-ipfs',
    'AtomSpaceIPFS': 'atomspace-ipfs',
    'atomspace-websockets': 'atomspace-websockets',
    'AtomSpaceWebSockets': 'atomspace-websockets',
    'atomspace-restful': 'atomspace-restful',
    'AtomSpaceRestful': 'atomspace-restful',
    'atomspace-bridge': 'atomspace-bridge',
    'AtomSpaceBridge': 'atomspace-bridge',
    'atomspace-metta': 'atomspace-metta',
    'AtomSpaceMetta': 'atomspace-metta',
    'atomspace-rpc': 'atomspace-rpc',
    'AtomSpaceRPC': 'atomspace-rpc',
    'python-attic': 'python-attic',
    'PythonAttic': 'python-attic',
    'atomese-simd': 'atomese-simd',
    'AtomeseSIMD': 'atomese-simd',
    'language-learning': 'language-learning',
    'LanguageLearning': 'language-learning',
    'profile': 'profile',
    'Profile': 'profile',
    'rocca': 'rocca',
    'ROCCA': 'rocca',
    'distributional-value': 'distributional-value',
    'DistributionalValue': 'distributional-value',
}

# External (system) dependencies
EXTERNAL_DEPS = {
    'Boost', 'boost', 'Cxxtest', 'cxxtest', 'Doxygen', 'doxygen',
    'VALGRIND', 'Valgrind', 'OpenSSL', 'openssl', 'Threads', 'threads',
    'Python3', 'Python', 'python', 'Guile', 'guile', 
    'PostgreSQL', 'pgsql', 'RocksDB', 'rocksdb',
    'UUID', 'uuid', 'Octomap', 'octomap',
    'OpenCV', 'opencv', 'OpenMP', 'openmp',
    'MPI', 'mpi', 'Folly', 'folly', 'OCaml', 'ocaml',
    'Stack', 'stack', 'GHC', 'ghc',
    'nlohmann_json', 'jsoncpp', 'ZMQ', 'zmq',
    'pkgconfig', 'PkgConfig', 'TBB', 'tbb',
    'GTest', 'gtest', 'GTK3', 'gtk3', 'GTK', 'gtk',
    'Festival', 'festival', 'EST', 'est',
    'ALSA', 'alsa', 'Protobuf', 'protobuf',
    'DLIB', 'dlib', 'PocketSphinx', 'pocketsphinx',
    'WiringPi', 'wiringpi', 'RaspiCam', 'raspicam',
    'GRPC', 'grpc', 'OpenDHT', 'opendht',
    'Catch2', 'catch2',
    # ROS packages
    'catkin', 'Catkin', 'roscpp', 'rospy', 'std_msgs',
}


class DependencyAnalyzer:
    """Analyzes OpenCog package dependencies"""
    
    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root)
        self.packages: Dict[str, Package] = {}
        self.dependency_graph: Dict[str, Set[str]] = defaultdict(set)
        self.reverse_graph: Dict[str, Set[str]] = defaultdict(set)
        
    def find_packages(self) -> List[str]:
        """Find all directories with CMakeLists.txt at the top level"""
        packages = []
        for item in self.repo_root.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                cmake_file = item / 'CMakeLists.txt'
                pkg_name = item.name
                if cmake_file.exists():
                    packages.append(pkg_name)
                    self.packages[pkg_name] = Package(
                        name=pkg_name, 
                        path=str(item.relative_to(self.repo_root)),
                        has_cmake=True
                    )
                elif item.name not in ['scripts', 'docs', 'docker', 'ci_artifacts', 
                                       'test-datasets', 'rest-api-documentation']:
                    # Track packages without CMakeLists.txt
                    self.packages[pkg_name] = Package(
                        name=pkg_name,
                        path=str(item.relative_to(self.repo_root)),
                        has_cmake=False
                    )
        return packages
    
    def parse_cmake_file(self, cmake_path: Path) -> Tuple[List[Dependency], Optional[str], Optional[str]]:
        """Parse a CMakeLists.txt file for dependencies"""
        dependencies = []
        cmake_version = None
        project_version = None
        
        try:
            content = cmake_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            print(f"Warning: Could not read {cmake_path}: {e}")
            return dependencies, cmake_version, project_version
        
        # Extract CMAKE_MINIMUM_REQUIRED version
        cmake_ver_match = re.search(
            r'CMAKE_MINIMUM_REQUIRED\s*\(\s*VERSION\s+([\d.]+)',
            content, re.IGNORECASE
        )
        if cmake_ver_match:
            cmake_version = cmake_ver_match.group(1)
        
        # Extract PROJECT version if present
        project_match = re.search(
            r'PROJECT\s*\(\s*\w+\s+VERSION\s+([\d.]+)',
            content, re.IGNORECASE
        )
        if project_match:
            project_version = project_match.group(1)
        
        # Find all FIND_PACKAGE directives
        # Pattern matches: FIND_PACKAGE(Name VERSION REQUIRED CONFIG)
        # Simplified pattern to avoid ReDoS - capture full content then parse
        find_pkg_pattern = re.compile(
            r'FIND_PACKAGE\s*\(\s*'
            r'(\w+)'                           # Package name
            r'([^)]*)'                         # Everything else until closing paren
            r'\)',
            re.IGNORECASE | re.MULTILINE
        )
        
        for match in find_pkg_pattern.finditer(content):
            pkg_name = match.group(1)
            args_str = match.group(2)
            full_match = match.group(0)
            
            # Parse version from args (first numeric-like token)
            version = None
            version_match = re.search(r'\b([\d.]+)\b', args_str)
            if version_match:
                version = version_match.group(1)
            
            required = 'REQUIRED' in full_match.upper()
            config_mode = 'CONFIG' in full_match.upper()
            
            dep = Dependency(
                name=pkg_name,
                version=version,
                required=required,
                config_mode=config_mode
            )
            dependencies.append(dep)
        
        return dependencies, cmake_version, project_version
    
    def analyze_all_packages(self):
        """Analyze all packages in the repository"""
        print(f"Analyzing packages in {self.repo_root}...")
        
        for pkg_name, pkg in self.packages.items():
            if not pkg.has_cmake:
                continue
                
            cmake_path = self.repo_root / pkg.path / 'CMakeLists.txt'
            deps, cmake_ver, proj_ver = self.parse_cmake_file(cmake_path)
            
            pkg.dependencies = deps
            pkg.cmake_version = cmake_ver
            pkg.project_version = proj_ver
            
            # Build dependency graph for internal deps
            for dep in deps:
                canonical_name = self.normalize_package_name(dep.name)
                if canonical_name and canonical_name in self.packages:
                    self.dependency_graph[pkg_name].add(canonical_name)
                    self.reverse_graph[canonical_name].add(pkg_name)
    
    def normalize_package_name(self, name: str) -> Optional[str]:
        """Convert a package name to its canonical form"""
        if name in OPENCOG_PACKAGES:
            return OPENCOG_PACKAGES[name]
        if name in EXTERNAL_DEPS:
            return None  # External dependency
        # Try case-insensitive match
        for key, value in OPENCOG_PACKAGES.items():
            if key.lower() == name.lower():
                return value
        return None
    
    def compute_tiers(self):
        """Compute dependency tiers using topological sort"""
        # Packages with no internal dependencies are tier 0
        in_degree = {pkg: 0 for pkg in self.packages if self.packages[pkg].has_cmake}
        
        # Calculate in-degrees: count how many packages depend on each package
        for pkg, deps in self.dependency_graph.items():
            if not self.packages.get(pkg, Package('', '')).has_cmake:
                continue
            for dep in deps:
                if dep in in_degree:
                    in_degree[dep] = in_degree.get(dep, 0) + 1
        
        # BFS to assign tiers
        current_tier = 0
        assigned = set()
        
        while len(assigned) < len([p for p in self.packages if self.packages[p].has_cmake]):
            # Find all packages with no remaining unassigned dependencies
            tier_packages = []
            for pkg in self.packages:
                if not self.packages[pkg].has_cmake or pkg in assigned:
                    continue
                deps = self.dependency_graph.get(pkg, set())
                unassigned_deps = deps - assigned
                # Only consider deps that have CMake
                unassigned_deps = {d for d in unassigned_deps if d in self.packages and self.packages[d].has_cmake}
                if not unassigned_deps:
                    tier_packages.append(pkg)
            
            if not tier_packages:
                # Circular dependency or remaining packages have missing deps
                remaining = set(p for p in self.packages if self.packages[p].has_cmake) - assigned
                print(f"Warning: Could not assign tier to: {remaining}")
                for pkg in remaining:
                    self.packages[pkg].tier = current_tier
                break
            
            for pkg in tier_packages:
                self.packages[pkg].tier = current_tier
                assigned.add(pkg)
            
            current_tier += 1
    
    def get_internal_dependencies(self, pkg_name: str) -> List[str]:
        """Get list of internal OpenCog dependencies for a package"""
        return list(self.dependency_graph.get(pkg_name, set()))
    
    def get_external_dependencies(self, pkg_name: str) -> List[Dependency]:
        """Get list of external dependencies for a package"""
        pkg = self.packages.get(pkg_name)
        if not pkg:
            return []
        
        external = []
        for dep in pkg.dependencies:
            if dep.name in EXTERNAL_DEPS or self.normalize_package_name(dep.name) is None:
                external.append(dep)
        return external
    
    def get_dependents(self, pkg_name: str) -> List[str]:
        """Get packages that depend on this package"""
        return list(self.reverse_graph.get(pkg_name, set()))
    
    def generate_report(self) -> dict:
        """Generate a complete dependency report"""
        # Group packages by tier
        tiers = defaultdict(list)
        for pkg_name, pkg in self.packages.items():
            if pkg.has_cmake:
                tiers[pkg.tier].append(pkg_name)
        
        # Build report
        report = {
            'summary': {
                'total_packages': len(self.packages),
                'packages_with_cmake': sum(1 for p in self.packages.values() if p.has_cmake),
                'packages_without_cmake': sum(1 for p in self.packages.values() if not p.has_cmake),
                'total_tiers': max(tiers.keys()) + 1 if tiers else 0,
            },
            'tiers': {},
            'packages': {},
            'dependency_graph': {},
            'reverse_graph': {},
            'build_order': [],
        }
        
        # Add tier information
        for tier_num in sorted(tiers.keys()):
            report['tiers'][f'tier_{tier_num}'] = sorted(tiers[tier_num])
        
        # Add package details
        for pkg_name, pkg in sorted(self.packages.items()):
            report['packages'][pkg_name] = {
                'path': pkg.path,
                'has_cmake': pkg.has_cmake,
                'cmake_version': pkg.cmake_version,
                'project_version': pkg.project_version,
                'tier': pkg.tier,
                'internal_dependencies': self.get_internal_dependencies(pkg_name),
                'external_dependencies': [d.to_dict() for d in self.get_external_dependencies(pkg_name)],
                'dependents': self.get_dependents(pkg_name),
            }
        
        # Add graph data
        for pkg, deps in self.dependency_graph.items():
            report['dependency_graph'][pkg] = sorted(deps)
        
        for pkg, deps in self.reverse_graph.items():
            report['reverse_graph'][pkg] = sorted(deps)
        
        # Generate build order (all packages in tier order)
        for tier_num in sorted(tiers.keys()):
            report['build_order'].extend(sorted(tiers[tier_num]))
        
        return report
    
    def print_summary(self):
        """Print a human-readable summary"""
        report = self.generate_report()
        
        print("\n" + "=" * 70)
        print("OpenCog Dependency Analysis Report")
        print("=" * 70)
        
        print(f"\n📊 Summary:")
        print(f"   Total packages: {report['summary']['total_packages']}")
        print(f"   With CMakeLists.txt: {report['summary']['packages_with_cmake']}")
        print(f"   Without CMakeLists.txt: {report['summary']['packages_without_cmake']}")
        print(f"   Build tiers: {report['summary']['total_tiers']}")
        
        print("\n📦 Packages by Tier:")
        for tier_name, packages in report['tiers'].items():
            tier_num = tier_name.split('_')[1]
            print(f"\n   Tier {tier_num} ({len(packages)} packages):")
            for pkg in packages:
                deps = self.get_internal_dependencies(pkg)
                dep_str = f" → depends on: {', '.join(deps)}" if deps else " (no internal deps)"
                print(f"      - {pkg}{dep_str}")
        
        print("\n⚠️  Packages without CMakeLists.txt:")
        no_cmake = [p for p in self.packages.values() if not p.has_cmake]
        for pkg in no_cmake:
            print(f"      - {pkg.name}")
        
        print("\n" + "=" * 70)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Analyze OpenCog package dependencies'
    )
    parser.add_argument(
        '--repo', '-r',
        default='.',
        help='Path to OpenCog repository root'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output file path (JSON or YAML based on extension)'
    )
    parser.add_argument(
        '--format', '-f',
        choices=['json', 'yaml', 'both'],
        default='both',
        help='Output format'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress summary output'
    )
    
    args = parser.parse_args()
    
    # Run analysis
    analyzer = DependencyAnalyzer(args.repo)
    analyzer.find_packages()
    analyzer.analyze_all_packages()
    analyzer.compute_tiers()
    
    # Generate report
    report = analyzer.generate_report()
    
    # Output results
    if not args.quiet:
        analyzer.print_summary()
    
    # Write to file(s)
    repo_root = Path(args.repo)
    
    if args.format in ['json', 'both']:
        output_path = args.output if args.output and args.output.endswith('.json') else \
                      repo_root / 'build' / 'dependency-graph.json'
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n✅ JSON report written to: {output_path}")
    
    if args.format in ['yaml', 'both']:
        output_path = args.output if args.output and args.output.endswith('.yaml') else \
                      repo_root / 'build' / 'dependency-graph.yaml'
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            yaml.dump(report, f, default_flow_style=False, sort_keys=False)
        print(f"✅ YAML report written to: {output_path}")
    
    return 0


if __name__ == '__main__':
    exit(main())
