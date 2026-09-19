### RunAnalysis execution environment

The 2023 EPD ADC distributions were regenerated using the legacy STAR calibration environment:

- STAR runtime: `SL24b`
- ROOT: `5.34/38`
- Architecture: 32-bit (`linux-rhel7-x86`, Intel 80386)
- Container/OS compatibility: STAR Scientific Linux 7 environment via Singularity

### Environment setup

```tcsh
starver SL24b
setup 32b
starver SL24b
setup 32b
./RunAnalysis.sh 167
```text
