# AGScanner - Automated Generation-based Scanner

##### AGScanner - new-generation fuzzing tool.

It allows you to perform a complete security audit of a website or API in terms of conducting fuzzing testing of entry points.

##### The tool consists of one main module and three auxiliary modules:

```
---| Main Module 
   |
   |--- Spy Module (a.k.a web crawler)
   |
   |--- Analyzer Module (finds entrypoints for fuzzing)
   |
   |--- Fuzzer Module (FUZZ!)
```
