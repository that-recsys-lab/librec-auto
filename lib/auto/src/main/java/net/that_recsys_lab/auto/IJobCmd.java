package net.that_recsys_lab.auto;

import net.librec.common.LibrecException;

import java.io.IOException;

@FunctionalInterface
public interface IJobCmd {
    public void execute() throws LibrecException, IOException, ClassNotFoundException;
}
