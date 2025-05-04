#include "pin.H"
#include <iostream>
#include <fstream>
#include <list>
#include <string>

using std::string;
using std::list;
using std::ofstream;
using std::endl;

class RTNNode {
public:
    RTN rtn;
    string rtnName;
    ADDRINT rtnAddr;
    string imgName;
    ADDRINT imgAddr;
    UINT64 instrCount = 0;
    UINT64 callCount = 0;

    RTNNode() = default;
    ~RTNNode() = default;
};

list<RTNNode*> rtnList;

VOID IncrementCounter(UINT64* counter) {
    (*counter)++;
}

bool CompareByInstructionCount(RTNNode* a, RTNNode* b) {
    return a->instrCount > b->instrCount;
}

VOID InstrumentRoutine(RTN rtn, VOID* v) {
    if (!RTN_Valid(rtn)) return;

    RTNNode* node = new RTNNode;
    node->rtn = rtn;
    node->rtnName = RTN_Name(rtn);
    node->rtnAddr = RTN_Address(rtn);

    IMG img = IMG_FindByAddress(node->rtnAddr);
    if (IMG_Valid(img)) {
        node->imgName = IMG_Name(img);
        node->imgAddr = IMG_LowAddress(img);
    }

    rtnList.push_back(node);

    RTN_Open(rtn);

    RTN_InsertCall(rtn, IPOINT_BEFORE, (AFUNPTR)IncrementCounter, IARG_PTR, &(node->callCount), IARG_END);

    for (INS ins = RTN_InsHead(rtn); INS_Valid(ins); ins = INS_Next(ins)) {
        INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)IncrementCounter, IARG_PTR, &(node->instrCount), IARG_END);
    }

    RTN_Close(rtn);
}

VOID WriteResults(INT32 code, VOID* v) {
    rtnList.sort(CompareByInstructionCount);

    ofstream outFile("rtn-output.csv");
    if (!outFile.is_open()) {
        std::cerr << "Error opening output file!" << endl;
        return;
    }

    for (RTNNode* node : rtnList) {
        if (node->callCount > 0) {
            outFile << node->imgName << ","
                    << "0x" << std::hex << node->imgAddr << ","
                    << node->rtnName << ","
                    << "0x" << std::hex << node->rtnAddr << ","
                    << std::dec << node->instrCount << ","
                    << node->callCount << endl;
        }
    }

    outFile.close();


    for (RTNNode* node : rtnList) {
        delete node;
    }
    rtnList.clear();
}

int main(int argc, char* argv[]) {
    PIN_InitSymbols();

    if (PIN_Init(argc, argv)) {
        std::cerr << "PIN_Init failed." << endl;
        return 1;
    }

    RTN_AddInstrumentFunction(InstrumentRoutine, nullptr);
    PIN_AddFiniFunction(WriteResults, nullptr);

    PIN_StartProgram();
    return 0;
}
