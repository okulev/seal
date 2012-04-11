// Copyright (C) 2011-2012 CRS4.
//
// This file is part of Seal.
//
// Seal is free software: you can redistribute it and/or modify it
// under the terms of the GNU General Public License as published by the Free
// Software Foundation, either version 3 of the License, or (at your option)
// any later version.
//
// Seal is distributed in the hope that it will be useful, but
// WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
// or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
// for more details.
//
// You should have received a copy of the GNU General Public License along
// with Seal.  If not, see <http://www.gnu.org/licenses/>.

package it.crs4.seal.demux;

import it.crs4.seal.common.ClusterUtils;
import it.crs4.seal.common.SealToolParser;

import java.util.ArrayList;
import java.io.IOException;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;

import org.apache.commons.cli.*;

public class DemuxOptionParser extends SealToolParser {

	public static final String ConfigSection = "Demux";

	private Option sampleSheetOpt;
	private Path sampleSheetPath;

	private Option laneContentOpt;
	private boolean createLaneContent;

	public DemuxOptionParser()
	{
		super(ConfigSection, "seal_demux");

		sampleSheetOpt = OptionBuilder
											.withDescription("Sample sheet for the experiment")
											.hasArg()
											.withArgName("FILE")
											.withLongOpt("sample-sheet")
											.create("s");
		options.addOption(sampleSheetOpt);

		laneContentOpt = OptionBuilder
											.withDescription("create LaneContent files")
											.withLongOpt("create-lane-content")
											.create("l");
		createLaneContent = false;
		options.addOption(laneContentOpt);

		this.setMinReduceTasks(1);
	}

	@Override
	protected CommandLine parseOptions(Configuration conf, String[] args)
	  throws IOException, ParseException
	{
		CommandLine line = super.parseOptions(conf, args);
		// options
		if (line.hasOption( sampleSheetOpt.getOpt() ))
		{
			sampleSheetPath = new Path(line.getOptionValue(sampleSheetOpt.getOpt()));
			if (sampleSheetPath.getFileSystem(conf).exists(sampleSheetPath))
			{
				sampleSheetPath = sampleSheetPath.makeQualified(sampleSheetPath.getFileSystem(conf));
				if ( !"hdfs".equals(sampleSheetPath.toUri().getScheme()) )
					throw new ParseException("Sample sheet must be on HDFS");
			}
			else
				throw new ParseException("Sample sheet " + sampleSheetPath.toString() + " doesn't exist");
		}
		else
			throw new ParseException("Missing --" + sampleSheetOpt.getLongOpt() + " argument");
		if (line.hasOption(laneContentOpt.getOpt()))
			createLaneContent = true;

		// set number of reduce tasks to use
		conf.set(ClusterUtils.NUM_RED_TASKS_PROPERTY, String.valueOf(getNReduceTasks()));
		return line;
	}

	public Path getSampleSheetPath() { return sampleSheetPath; }

	public boolean getCreateLaneContent() { return createLaneContent; }
}
