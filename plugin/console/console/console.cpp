#include <iostream>
#include <Windows.h>

using namespace std;

int main(int argc, char* argv[])
{
    if (argc>1)
    {
        char* title = argv[1];
        cout << title << endl;
        SetConsoleTitleA(title); 

    }
    const int size = 40960;
    const char endLine[] = "console exit";
    const char emptyLine[] = "";
    char line[size];
    
    while (true)
    {
        cin.getline(line, size);
        if (strcmp(line, endLine) == 0)
            break;
        if (strcmp(line, emptyLine) == 0)
            continue;
        cout << line << endl;
    }
}

