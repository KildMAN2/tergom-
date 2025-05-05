#include <fstream>
#include <iomanip>
#include <iostream>
#include <string.h>
#include <map>
#include <vector>
#include <algorithm>
#include "pin.H"

using std::cerr;
using std::endl;
using std::hex;
using std::dec;
using std::ofstream;
using std::string;
using std::map;
using std::pair;
using std::vector;

ofstream outFile;

struct BBLInfo {
    UINT64 execCount = 0;
    UINT64 takenCount = 0;
    UINT64 fallthroughCount = 0;
    map<ADDRINT, UINT64> indirectTargets;
};

map<ADDRINT, BBLInfo> bblMap;

VOID CountBBL(ADDRINT bblAddr) {
    bblMap[bblAddr].execCount++;
}

VOID CountConditional(ADDRINT bblAddr, BOOL taken) {
    if (taken)
        bblMap[bblAddr].takenCount++;
    else
        bblMap[bblAddr].fallthroughCount++;
}

VOID CountIndirect(ADDRINT bblAddr, ADDRINT targetAddr) {
    bblMap[bblAddr].indirectTargets[targetAddr]++;
}

VOID TraceBasicBlock(TRACE trace, VOID* v) {
    for (BBL bbl = TRACE_BblHead(trace); BBL_Valid(bbl); bbl = BBL_Next(bbl)) {
        ADDRINT bblAddr = BBL_Address(bbl);

        BBL_InsertCall(bbl, IPOINT_ANYWHERE, (AFUNPTR)CountBBL, IARG_ADDRINT, bblAddr, IARG_END);

        INS tail = BBL_InsTail(bbl);

        if (INS_IsBranch(tail) && INS_HasFallThrough(tail)) {
            INS_InsertCall(tail, IPOINT_BEFORE, (AFUNPTR)CountConditional, IARG_ADDRINT, bblAddr, IARG_BRANCH_TAKEN, IARG_END);
        }
        else if (INS_IsIndirectBranchOrCall(tail)) {
            INS_InsertCall(tail, IPOINT_BEFORE, (AFUNPTR)CountIndirect, IARG_ADDRINT, bblAddr, IARG_BRANCH_TARGET_ADDR, IARG_END);
        }
    }
}

bool CompareBBL(pair<ADDRINT, BBLInfo>& a, pair<ADDRINT, BBLInfo>& b) {
    return a.second.execCount > b.second.execCount;
}

VOID Fini(INT32 code, VOID* v) {
    vector<pair<ADDRINT, BBLInfo>> sortedBBLs(bblMap.begin(), bblMap.end());
    std::sort(sortedBBLs.begin(), sortedBBLs.end(), CompareBBL);

    outFile.open("edge-profile.csv");

    for (auto& entry : sortedBBLs) {
        ADDRINT addr = entry.first;
        BBLInfo& info = entry.second;

        if (info.execCount == 0) continue;

        outFile << hex << "0x" << addr << dec << ", " << info.execCount;

        if (info.takenCount + info.fallthroughCount > 0) {
            outFile << ", " << info.takenCount << ", " << info.fallthroughCount;
        } else {
            outFile << ", , ";
        }

        if (!info.indirectTargets.empty()) {
            vector<pair<ADDRINT, UINT64>> targets(info.indirectTargets.begin(), info.indirectTargets.end());
            std::sort(targets.begin(), targets.end(), [](auto& a, auto& b) { return a.second > b.second; });
            int count = 0;
            for (auto& t : targets) {
                if (count >= 10) break;
                outFile << ", 0x" << hex << t.first << dec << ", " << t.second;
                count++;
            }
        }

        outFile << endl;
    }

    outFile.close();
}

int main(int argc, char* argv[]) {
    PIN_InitSymbols();
    if (PIN_Init(argc, argv)) {
        cerr << "Usage: pin -t ex2.so -- <program>" << endl;
        return -1;
    }

    TRACE_AddInstrumentFunction(TraceBasicBlock, 0);
    PIN_AddFiniFunction(Fini, 0);

    PIN_StartProgram();

    return 0;
}

